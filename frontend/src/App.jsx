import { useState } from 'react';
import { AppShell, Loader, Alert, Stack, Text } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { Sidebar } from './components/Sidebar';
import { UploadArea } from './components/UploadArea';
import { StatsDashboard } from './components/StatsDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState(1); // 1 = Upload tab
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = async (file) => {
    setUploadedFile(file);
    setIsAnalyzing(true);
    setError(null);

    // 1. prepare data for sending
    const formData = new FormData();
    formData.append("file", file); // "file" is a key that backend expects

    try {
        console.log("Sending file to backend...");

        // send request to local FastAPI backend
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        // receive json response with analysis results
        const data = await response.json();
        console.log("Analysis complete:", data);

        setAnalysisResult(data); // save results to state
        setActiveTab(2); // switch to dashboard tab to show results

    } catch (err) {
        console.error("Upload failed:", err);
        setError("Failed to process video. Make sure backend is running.");
        setUploadedFile(null); // reset file selection on error case
    } finally {
        setIsAnalyzing(false);
    }
  };

  return (
    <AppShell
      navbar={{ width: 80, breakpoint: 'sm' }}
      padding="md"
      style={{ background: '#f8f9fa' }}
    >
      <AppShell.Navbar p="0" style={{ borderRight: 0 }}>
        <Sidebar activeIndex={activeTab} setActiveIndex={setActiveTab} />
      </AppShell.Navbar>

      <AppShell.Main>
        {/* show error */}
        {error && (
            <Alert variant="light" color="red" title="Error" icon={<IconAlertCircle />} mb="lg" onClose={() => setError(null)} withCloseButton>
              {error}
            </Alert>
        )}

        {/* 1. loading display */}
        {activeTab === 1 && !uploadedFile && !isAnalyzing && (
            <div style={{ height: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <UploadArea onFileSelected={handleFileSelect} isLoading={isAnalyzing} />
            </div>
        )}

        {/* 2. spinner */}
        {isAnalyzing && (
            <div style={{ height: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <Stack align="center">
                    <Loader size="xl" type="bars" color="violet" />
                    <Text size="xl" fw={500} mt="md">Analyzing video...</Text>
                    <Text c="dimmed" size="sm">This may take some time...</Text>
                </Stack>
            </div>
        )}

        {/* 3. analysis results (Dashboard) */}
        {activeTab === 2 && analysisResult && (
            // send real data from backend to dashboard component to display stats
            <StatsDashboard data={analysisResult} filename={uploadedFile?.name} />
        )}
      </AppShell.Main>
    </AppShell>
  );
}