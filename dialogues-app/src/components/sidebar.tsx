import React from "react";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Link from "@mui/material/Link";
import IconButton from "@mui/material/IconButton";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import "../index.css";


interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  guardrailValues: Record<string, number>;
}

const drawerWidth = 360; // Width when sidebar is open
const collapsedWidth = 120;

const Sidebar: React.FC<SidebarProps> = ({
  sidebarOpen,
  setSidebarOpen,
}) => (
  <Drawer
    variant="permanent"
    className={`sidebar-drawer ${sidebarOpen ? "sidebar-drawer-open" : "sidebar-drawer-collapsed"}`}
    PaperProps={{ elevation: 3, className: `sidebar-drawer ${sidebarOpen ? "sidebar-drawer-open" : "sidebar-drawer-collapsed"}` }}
  >
    <Box className={`sidebar-header${!sidebarOpen ? " sidebar-header-collapsed" : ""}`}>
      <IconButton onClick={() => setSidebarOpen(!sidebarOpen)} size="large" className="sidebar-arrow">
        {sidebarOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
      </IconButton>
    </Box>
    {sidebarOpen ? (
      <>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          💬 Dialogues between Human and Machine.
        </Typography>
        <Divider className="sidebar-divider" />

        <Box className="sidebar-info">
          ℹ️ We believe that humans should be in the loop when it comes to Artificial Intelligence, both explicitly and implicitly. 
          Thus, human values, virtues, and guardrails need to be baked into the core of AI systems. 
          This application showcases how this can be done, deriving and approximating these guardrails and values 
          from data around human perspectives and expectations for AI systems. The guardrails are then used to tailor and customize 
          a range of prompt templates of a Large Language Model. You want to know more or want to contribute to this project - head over to our{" "}
          <Link href="https://github.com/schutera/informedDialogues" target="_blank" rel="noopener">
            GitHub
          </Link>. 
        </Box>
        <Box className="sidebar-info2">
          💾 The solution is tailored and built upon {" "}
          <Link href="https://globaldialogues.ai/" target="_blank" rel="noopener">
            Global Dialogues
          </Link> Data. Provided by the "A Collective Intelligence Project". Last accessed on 2025-06-18.
        </Box>
        <Box className="sidebar-info3">
          ⚡by the kids and wizards over{" "}
          <Link href="https://partner.schutera.com/" target="_blank" rel="noopener">
            here
          </Link>. Reach out if you want us to build something for you.
        </Box>
      </>
    ) : null}
  </Drawer>
);

export default Sidebar;