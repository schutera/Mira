# This code is adapted and originally from:
# https://colab.research.google.com/drive/1VEaRt7qCQGRuL77rdiMc7koqAAg-AwgE?usp=sharing#scrollTo=vICZNUUf9TPA

import pandas as pd
import csv
import warnings
import math
import json
import matplotlib.pyplot as plt
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI
import os

warnings.filterwarnings('ignore')
plt.close("all")
client = OpenAI()

# Constants
PADDING_ROWS = 9  # Number of non-content rows before the initial column headers in the CSV
pd.set_option('display.max_colwidth', 0)

def p2f(x):
    """
    Convert percentage string to float.
    """
    try:
        if x == ' - ':
            return float("nan")
        else:
            return float(x.strip('%')) / 100
    except:
        return x

def load_csv_data(filename):
    """
    Load and process data from a CSV file.

    Args:
        filename (str): Path to the CSV file.

    Returns:
        tuple: A tuple containing:
            - List of DataFrames for each question (qs)
            - Metadata DataFrame (qmeta)
    """
    with open(filename, 'r', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        r = 1
        data = []
        qdata = []
        for row in csvreader:
            if r > PADDING_ROWS:
                if len(row) == 0 or not row[0].strip():
                    data.append(qdata)
                    qdata = []
                else:
                    qdata.append(row)
            r += 1
        data.append(qdata)

    # Handle blank row
    data = data[1:]

    # Process data
    nq = len(data)
    qs = []
    meta = [["question type", "question text"]]
    for i in range(nq):
        d = data[i]
        m = [d[1][1], d[1][2]]
        meta.append(m)
        if d[1][1] == 'Poll Single Select':
            for r in range(1, len(d)):
                for c in range(4, len(d[0])):
                    d[r][c] = p2f(d[r][c])
        if d[1][1] == 'Ask Opinion':
            for r in range(1, len(d)):
                for c in range(6, len(d[0]) - 3):
                    d[r][c] = p2f(d[r][c])
        df = pd.DataFrame(d[1:], columns=d[0])
        qs.append(df)
    qmeta = pd.DataFrame(meta[1:], columns=meta[0])

    return qs, qmeta

# ----------------------------------
# function to show the questions by ID
def show_questions(qs_):
    questions = [["question type", "question text"]]
    for i in range(0, len(qs_)):
        questions.append([qs_[i]["Question Type"][1], qs_[i]["Question"][1]])
    return pd.DataFrame(questions[1:], columns=questions[0])

# ----------------------------------
# function to show the segments by ID
def show_segments(qs_):
    segments = []
    q0 = qs_[0]
    if q0["Question Type"][1] == 'Poll Single Select':
        for c in range(4, len(q0.columns)):
            segments.append(q0.columns[c])
    if q0["Question Type"][1] == 'Ask Opinion':
        for c in range(5, len(q0.columns) - 3):
            segments.append(q0.columns[c])
    return pd.DataFrame(segments)

# ----------------------------------
# function to plot poll data by segment
def plot_poll(df, segs):
    print(df["Question"][1])
    segs_incl = ['Responses']
    for i in range(0, len(segs)):
        segs_incl.append(df.columns[4 + segs[i]])
    dfplt = df[segs_incl]
    dfplt = dfplt.set_index('Responses')
    dfplt.plot.barh()
    return dfplt

# ----------------------------------
# function to make a results table dataframe look prettier
def make_pretty(styler):
    styler.background_gradient(axis=None, vmin=0, vmax=1, cmap="RdYlGn")
    styler.format(precision=2)
    return styler

# ----------------------------------
# function to generate a results table for an opinion ask for a given set of segments
def table_ask(df, segs, n):
    segs_incl = ['English Responses']
    for i in range(0, len(segs)):
        segs_incl.append(df.columns[7 + segs[i]])
    dfplt = df[segs_incl]
    return dfplt.iloc[:n].style.pipe(make_pretty)

# ----------------------------------
# compute max-min bridging metric, used in bridging_ask function
def min_bridge(row, segs_incl, col):
    b = 1
    for s in range(0, len(segs_incl)):
        b_ = row[segs_incl[s]]
        b = min(b, b_)
    return b

# ----------------------------------
# compute max-min polarization metric, used in bridging_ask function
def polarization(row, segs_incl, col):
    mx = 0
    mn = 1
    for s in range(0, len(segs_incl)):
        b_ = row[segs_incl[s]]
        mx = max(mx, b_)
        mn = min(mn, b_)
    return mx - mn

# ----------------------------------
# compute max-min divergence metric, used in bridging_ask function
def symmetric_divergence(row, segs_incl, col):
    mx = 0
    mn = 1
    for s in range(0, len(segs_incl)):
        b_ = row[segs_incl[s]]
        mx = max(mx, b_)
        mn = min(mn, b_)
    mx_div = max(mx - 0.5, 0)
    mn_div = max(0.5 - mn, 0)
    return math.sqrt(mx_div * mn_div)

# ----------------------------------
# generate dataframe which includes bridging, polarization, divergence metrics
def bridging_ask(df, segs):
    segs_incl = ['English Responses']
    for i in range(0, len(segs)):
        segs_incl.append(df.columns[7 + segs[i]])
    dfplt = df[segs_incl].copy()
    dfplt["bridge"] = df.apply(lambda row: min_bridge(row, segs_incl[1:], df.columns), axis=1)
    dfplt["polarization"] = df.apply(lambda row: polarization(row, segs_incl[1:], df.columns), axis=1)
    dfplt["divergence"] = df.apply(lambda row: symmetric_divergence(row, segs_incl[1:], df.columns), axis=1)
    return dfplt.sort_values(by=["bridge"], ascending=False)

# ----------------------------------
# function to get responses whose bridging agreement across a given set of segments is over a specified threshold
def get_bridging_responses(df, segs, thresh):
    bdf = bridging_ask(df, segs)
    return bdf.loc[bdf['bridge'] > thresh]

# ----------------------------------
# function to get the top n responses with highest polarization across a set of segments
def get_polarizing_responses(df, segs, n):
    bdf = bridging_ask(df, segs)
    bdfp = bdf.sort_values(by=["polarization"], ascending=False)
    return bdfp.iloc[:n]

# ----------------------------------
# function to get the top n responses with most divergent responses across a set of segments
def get_divergent_responses(df, segs, n):
    bdf = bridging_ask(df, segs)
    bdfp = bdf.sort_values(by=["divergence"], ascending=False)
    return bdfp.iloc[:n]

# ----------------------------------
# generate a text summary of the n responses with the highest polarization
def polarization_summary(df, segs, n):
    pa = get_polarizing_responses(df, segs, n)
    temp_pa = pa.iloc[:, 1:-2]
    min_col = temp_pa.idxmin(axis=1)
    max_col = temp_pa.idxmax(axis=1)
    min_val = temp_pa.min(axis=1)
    max_val = temp_pa.max(axis=1)
    for idx in pa.index:
        first_col_text = pa.loc[idx, pa.columns[0]]
        min_col_name = min_col.loc[idx]
        max_col_name = max_col.loc[idx]
        min_value = pa.loc[idx, min_col_name]
        max_value = pa.loc[idx, max_col_name]
        print(first_col_text)
        print("Low : " + str(int(min_value * 100)) + "% -- " + min_col_name)
        print("High : " + str(int(max_value * 100)) + "% -- " + max_col_name)
        print(" ")

# ----------------------------------
# generate a text summary of the n responses with the highest (symetric) divergence
def divergence_summary(df, segs, n):
    pa = get_divergent_responses(df, segs, n)
    temp_pa = pa.iloc[:, 1:-2]
    min_col = temp_pa.idxmin(axis=1)
    max_col = temp_pa.idxmax(axis=1)
    min_val = temp_pa.min(axis=1)
    max_val = temp_pa.max(axis=1)
    for idx in pa.index:
        first_col_text = pa.loc[idx, pa.columns[0]]
        min_col_name = min_col.loc[idx]
        max_col_name = max_col.loc[idx]
        min_value = pa.loc[idx, min_col_name]
        max_value = pa.loc[idx, max_col_name]
        print(first_col_text)
        print("Low : " + str(int(min_value * 100)) + "% -- " + min_col_name)
        print("High : " + str(int(max_value * 100)) + "% -- " + max_col_name)
        print(" ")

# ----------------------------------
# function to save qs as a json object that can be reloaded via json import above
def save_qs_to_json(qs, filename):
    qx = []
    for i in range(0, len(qs)):
        qx.append(qs[i].to_dict())
    with open(filename, 'w') as f:
        json.dump(qx, f)

# ----------------------------------
# function to load qs from a json object saved by the above function
def load_qs_from_json(filename):
    with open(filename, 'r') as f:
        qx = json.load(f)
    qs = []
    for i in range(0, len(qx)):
        qs.append(pd.DataFrame.from_dict(qx[i]))
    return qs

# ----------------------------------
# compute and show the distribution of responses for a question across segments
def response_distribution(qs_, segs, qid):
    import matplotlib.pyplot as plt
    df = qs_[qid]
    if df["Question Type"][1] == 'Poll Single Select':
        segs_incl = ['Responses']
        for i in range(0, len(segs)):
            segs_incl.append(df.columns[4 + segs[i]])
        dfplt = df[segs_incl]
        dfplt = dfplt.set_index('Responses')
        ax = dfplt.plot.barh()
        plt.title(df["Question"][1])
        plt.xlabel("Percent of Responses")
        plt.ylabel("Response Options")
        plt.legend(title="Segments")
        return ax
    if df["Question Type"][1] == 'Ask Opinion':
        segs_incl = ['English Responses']
        for i in range(0, len(segs)):
            segs_incl.append(df.columns[7 + segs[i]])
        dfplt = df[segs_incl]
        dfplt = dfplt.set_index('English Responses')
        ax = dfplt.plot.barh()
        plt.title(df["Question"][1])
        plt.xlabel("Percent of Responses")
        plt.ylabel("Response Options")
        plt.legend(title="Segments")
        return ax

# ----------------------------------
# function to compute and show the change in response distribution between two segments for a question
def response_change(qs_, segs, qid, seg_a, seg_b):
    import matplotlib.pyplot as plt
    df = qs_[qid]
    if df["Question Type"][1] == 'Poll Single Select':
        dfplt = df[['Responses', df.columns[4 + seg_a], df.columns[4 + seg_b]]]
        dfplt = dfplt.set_index('Responses')
        dfplt = dfplt.rename(columns={df.columns[4 + seg_a]: "Segment " + str(seg_a), df.columns[4 + seg_b]: "Segment " + str(seg_b)})
        ax = dfplt.plot.barh()
        plt.title(df["Question"][1] + " (Segments " + str(seg_a) + " vs " + str(seg_b) + ")")
        plt.xlabel("Percent of Responses")
        plt.ylabel("Response Options")
        plt.legend(title="Segments")
        return ax
    if df["Question Type"][1] == 'Ask Opinion':
        dfplt = df[['English Responses', df.columns[7 + seg_a], df.columns[7 + seg_b]]]
        dfplt = dfplt.set_index('English Responses')
        dfplt = dfplt.rename(columns={df.columns[7 + seg_a]: "Segment " + str(seg_a), df.columns[7 + seg_b]: "Segment " + str(seg_b)})
        ax = dfplt.plot.barh()
        plt.title(df["Question"][1] + " (Segments " + str(seg_a) + " vs " + str(seg_b) + ")")
        plt.xlabel("Percent of Responses")
        plt.ylabel("Response Options")
        plt.legend(title="Segments")
        return ax

# ----------------------------------
# Embedding and LLM utilities

def get_embedding(text, model="text-embedding-3-small", dimensions=1024):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model, dimensions=dimensions).data[0].embedding

def embed_response(row):
    text = row["English Responses"]
    return get_embedding(text)

def embed_responses(df):
    df["embedding"] = df.apply(lambda row: embed_response(row), axis=1)
    return df

def add_embeddings_for_all_responses(qs):
    questions = show_questions(qs)
    oe_ids = []
    for i in range(0, len(questions)):
        if "Ask" in questions.iloc[i][0]:
            oe_ids.append(i)
            qs[i] = embed_responses(qs[i])
            print(i)
    return qs

def rank_by_similarity(qs, text):
    new_embedding = get_embedding(text)
    qs_copy = qs.copy()
    embedding_dim = len(new_embedding)
    embeddings = np.array([
        np.zeros(embedding_dim) if isinstance(embedding, float) and np.isnan(embedding) else embedding
        for embedding in qs_copy['embedding'].values
    ])
    similarities = cosine_similarity([new_embedding], embeddings)[0]
    qs_copy['cosine_similarity'] = similarities
    qs_sorted = qs_copy.sort_values(by='cosine_similarity', ascending=False)
    return qs_sorted

# LLM Chains and PromptTemplates

llm = ChatOpenAI(temperature=0.2, model_name='gpt-4-0125-preview')

rerankPrompt = PromptTemplate(
    input_variables=["question", "responses", "query"],
    template="""
    Participants in a research study were asked '{question}'.

    These are their responses:
    {responses}

    Filter the responses, keeping only the responses that are atleast somewhat related to or helpful in anwsering: {query}
    Rank the filtered resposnes starting with the most related to or helpful in answering: {query}
    Output this set of responses formated exactly in the way they are given above, with a newline spereate each response.
    If there are no related response, output "there are no relevant responses"
    """
)
rerankChain = LLMChain(llm=llm, prompt=rerankPrompt, output_key="reranked_responses")

summaryPrompt = PromptTemplate(
    input_variables=["question", "responses", "focus"],
    template="""
    Participants in a research study were asked '{question}'.

    These are their responses:
    {responses}

    Create a hierarchical taxonomy of the unique ideas and themes within these responses using very short bullet points. Avoid dupliate ideas. If there are no responses to analyze, do not provide a taxonomy. Do not include anything in the taxonomy not inlcuded in the responses.
    {focus}
    """
)
summaryChain = LLMChain(llm=llm, prompt=summaryPrompt, output_key="summary")

bulletsPrompt = PromptTemplate(
    input_variables=["question", "summary", "focus"],
    template="""
    Participants in a research study were asked '{question}'.

    The TAXONOMY of ideas in participants responses are:
    {summary}

    Summarize the TAXONOMY into 1-15 concise bullet points, with each bullet point starting with a single theme and then overviewing the ideas within that theme. Be direct and specific, DO NOT say things like "Particpants said" or "responses" or "there was a desire" or "this theme" or "focusing on". Just say the ideas. NEVER repeat a theme or idea. A theme name should not include "and". Each bullet should be very short. Each bullets must ONLY contain ideas from the taxonomy. If there is no taxonomy, just output "no ideas to synthesize"

    {focus}

    Example bullet points:
    - Creaive outlets: music, drawing, painting, writing stories, designing houses, creating new receipes, home remodeling.
    - Health improvement: Increased exercise, better diets, access to high-quality healthcare, and reduction of chronic diseases.
    """
)
bulletsChain = LLMChain(llm=llm, prompt=bulletsPrompt, output_key="bullets")

outcomePrompt = PromptTemplate(
    input_variables=["question", "summary", "responses"],
    template="""
    Participants in a research study were asked '{question}'.

    These are their responses:
    {responses}

    The main ideas from these responses are:
    {summary}

    We define an 'outcome' to be a single specific concrete result that can be observed and measured in the world. An 'outcome' should NOT include an explination of how it is acheived (ie. an 'outcome' should NOT include the words "due to" or "as a result of" or "through" or "by" etc.). An 'outcome' MUST be specific enough to be objectively observed or measured.

    Write a list of the 'outcomes' present in the main ideas from the responses summarized above. DO NOT REPEAT ANY IDEAS.

    Here are some examples of 'outcomes':

    - Earths climate remains below 15C
    - The number of gun deaths decreases to below 100 per day globally
    - The fraction of people who cannot afford or access healthcare decreases
    - No nuclear devices are detonated within 100 miles of a human
    - More people report being happy with their life

    """
)
outcomeChain = LLMChain(llm=llm, prompt=outcomePrompt, output_key="outcomes")

valuePrompt = PromptTemplate(
    input_variables=["question", "summary", "responses"],
    template="""
    Participants in a research study were asked '{question}'.

    These are their responses:
    {responses}

    The main ideas from these responses are:
    {summary}

    We define a 'value' to be a deontilogical property that can be reflected on how an AI behaves, reguardless of the result of that behavior. We do not consider a specific AI behavior to be a 'value'. For example "non-judegment: the AI's behavior does not imply a value judgement about the users feelings or experience" IS a 'value' , but "the AI does not say 'I am judgeing you'" is NOT a 'value'.

    Write a list of the unique 'values' present in the  main ideas from the responses summarized above.

    Here are some example 'values':

    - Empathy: Showing understanding and compassion to make the user feel heard and supported.
    - Respect: Honoring the user's feelings and experiences without minimizing their pain or struggles.
    - Non-judgment: Providing support without criticism or bias to create a safe space for the user to express themselves.

    DO NOT COPY THE EXAMPLE 'values' ABOVE VERBATIM. Construct them based on the responses and summarized ideas above.

    """
)
valueChain = LLMChain(llm=llm, prompt=valuePrompt, output_key="values")

genSummaryChain = SequentialChain(
    chains=[summaryChain],
    input_variables=["question", "responses", "focus"],
    output_variables=["summary"],
    verbose=False)

genOutcomeChain = SequentialChain(
    chains=[summaryChain, outcomeChain],
    input_variables=["question", "responses", "focus"],
    output_variables=["summary", "outcomes"],
    verbose=False)

genValuesChain = SequentialChain(
    chains=[summaryChain, valueChain],
    input_variables=["question", "responses", "focus"],
    output_variables=["summary", "values"],
    verbose=False)

genBulletsChain = SequentialChain(
    chains=[summaryChain, bulletsChain],
    input_variables=["question", "responses", "focus"],
    output_variables=["summary", "bullets"],
    verbose=False)

rerankOnlyChain = SequentialChain(
    chains=[rerankChain],
    input_variables=["question", "responses", "query"],
    output_variables=["reranked_responses"],
    verbose=False)

def synthesize(qs, qid, segs, synth_type, rank_type, thresh, n_max, query_text=""):
    if rank_type == "bridging":
        print("ranking by bridging")
        ba_ = get_bridging_responses(qs[qid], segs, thresh)
        ba = ba_.iloc[:n_max]
    elif rank_type == "polarization":
        print("ranking by polarization")
        ba = get_polarizing_responses(qs[qid], segs, n_max)
    elif rank_type == "divergence":
        print("ranking by divergence")
        ba = get_divergent_responses(qs[qid], segs, n_max)
    elif rank_type == "low_agreement":
        print("ranking by low agreement")
        ba_ = bridging_ask(qs[qid], segs)
        ba_ = ba_.sort_values(by=["bridge"], ascending=True)
        ba_ = ba_.loc[ba_["bridge"] < thresh]
        ba = ba_.iloc[:n_max]
    elif rank_type == "relevance":
        ba_ = rank_by_similarity(qs[qid], query_text)
        ba_ = ba_.loc[ba_["cosine_similarity"] > thresh]
        ba = ba_.iloc[:n_max]
    else:
        print("random sampling")
        ba_ = get_bridging_responses(qs[qid], segs, 0)
        ba = ba_.sample(n=n_max)

    responses_str = ''
    for ind in ba.index:
        rsp = ba["English Responses"][ind]
        responses_str += "-"
        responses_str += rsp
        responses_str += "\n \n "

    df = qs[qid]
    question_str = df["Question"][1]

    if query_text != "":
        focus = "only include topics and themes that are reasonably relevant to: " + query_text
        prelim_responses = rerankOnlyChain({
            "question": question_str,
            "responses": responses_str,
            "query": query_text
        })
        responses_str = prelim_responses["reranked_responses"]
    else:
        focus = ""

    if synth_type == "outcomes":
        out = genOutcomeChain({
            "question": question_str,
            "responses": responses_str,
            "focus": focus
        })
    if synth_type == "values":
        out = genValuesChain({
            "question": question_str,
            "responses": responses_str,
            "focus": focus
        })
    if synth_type == "bullets":
        out = genBulletsChain({
            "question": question_str,
            "responses": responses_str,
            "focus": focus
        })
    if synth_type == "summary":
        out = genSummaryChain({
            "question": question_str,
            "responses": responses_str,
            "focus": focus
        })
    out["data"] = ba
    return out

def embed_responses_and_save(df, qid, embeddings_dir="datasets/embeddings"):
    """
    Embed responses in the DataFrame and save the DataFrame with embeddings as a pickle.
    """
    os.makedirs(embeddings_dir, exist_ok=True)
    # Only embed if not already present
    if 'embedding' not in df.columns:
        df = embed_responses(df)
        # Save embeddings DataFrame as pickle
        pickle_path = os.path.join(embeddings_dir, f"embeddings_qid{qid}.pkl")
        df.to_pickle(pickle_path)
        print(f"Embeddings for qid {qid} saved to {pickle_path}")
    return df

if __name__ == "__main__":
    filename = "datasets/aggregate.csv"
    print(f"Loading CSV data from {filename}...")
    qs, qmeta = load_csv_data(filename)
    print("CSV data loaded successfully.")

    # Select question and segments
    qid = 16
    segs = [231, 232, 233, 234, 235, 236]

    print(f"Selected question ID: {qid}")
    question_text = qs[qid]["Question"][1]
    print(f"Question text: {question_text}")
    print(f"Selected segments: {segs}")

    # Load embeddings if available, otherwise embed and save
    embeddings_dir = "datasets/embeddings"
    pickle_path = os.path.join(embeddings_dir, f"embeddings_qid{qid}.pkl")
    if os.path.exists(pickle_path):
        print(f"Embeddings file found at {pickle_path}. Loading embeddings...")
        qs[qid] = pd.read_pickle(pickle_path)
        print(f"Loaded embeddings for qid {qid} from {pickle_path}")
    else:
        print(f"Embeddings file not found at {pickle_path}. Generating embeddings...")
        qs[qid] = embed_responses_and_save(qs[qid], qid)
        print(f"Embeddings generated and saved for qid {qid}.")

    # Set synthesis parameters
    synth_type = "bullets"      # Synthesize results as bullet points
    rank_type = "bridging"      # Ranking responses by bridging agreement across segs
    thresh = 0.25               # Lower threshold to 25% agreement across segments for broader inclusion
    n_max = 50                  # Only keep the top 10 responses with highest bridging agreement
    query_text = "AI guardrails and values"
    # Print synthesis parameters
    print(f"Synthesis parameters set:")
    print(f"  Synthesis type: {synth_type}")
    print(f"  Ranking type: {rank_type}")
    print(f"  Threshold: {thresh}")
    print(f"  Max responses: {n_max}")
    print(f"  Query text: {query_text}")

    # Run the synthesis
    print("Running synthesis...")
    out = synthesize(qs, qid, segs, synth_type, rank_type, thresh, n_max, query_text=query_text)
    print("Synthesis completed.")

    # Save synthesis results to a CSV file
    synthesis_csv_path = os.path.join("datasets", f"synthesis_qid{qid}_{synth_type}.csv")
    print(f"Saving synthesis {synth_type} results to {synthesis_csv_path}...")
    out["data"].to_csv(synthesis_csv_path, index=False)
    print(f"Synthesis {synth_type} results saved to {synthesis_csv_path}")

    # Save synthesis results to a CSV file
    synthesis_csv_path = os.path.join("datasets", f"synthesis_qid{qid}.csv")
    print(f"Saving synthesis results to {synthesis_csv_path}...")
    out["data"].to_csv(synthesis_csv_path, index=False)
    print(f"Synthesis results saved to {synthesis_csv_path}")

