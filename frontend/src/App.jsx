import { useState } from 'react';
import axios from 'axios';
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
      setUploadedFile((file));
    setIsAnalyzing(true);
    const chunkSize = 10 * 1024 * 1024; // 10 mb for one chunk
    const totalChunks = Math.ceil(file.size / chunkSize);

    try {
        for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);

            const formData = new FormData();
            formData.append("chunk", chunk);
            formData.append("chunkIndex", i);
            formData.append("filename", file.name);

            // send each chunk to backend
            await axios.post("http://127.0.0.1:8000/upload-chunk", formData);

            const progress = Math.round(((i + 1) / totalChunks) * 100);
            console.log(`Loaded chunk ${i + 1} of ${totalChunks} (${progress}%)`);
        }

        // start analysis after all chunks are uploaded
        const finalResponse = await axios.post("http://127.0.0.1:8000/analyze", {
            filename: file.name
        });

        setAnalysisResult(finalResponse.data);
        setActiveTab(2); // switch to dashboard tab
    } catch (err) {
        console.error("Error while uploading chunks:", err);
        setError("Uploading stopped.");
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