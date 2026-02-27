import { useState } from 'react';
import axios from 'axios';
import { AppShell, Loader, Alert, Stack, Text } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { UploadArea } from './components/UploadArea';
import { StatsDashboard } from './components/StatsDashboard';


function AnalysisLoader() {
  return (
    <div style={{ height: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <Stack align="center">
        <Loader size="xl" type="bars" color="violet" />
        <Text size="xl" fw={500} mt="md">Аналізуємо відео...</Text>
      </Stack>
    </div>
  );
}

function AppContent() {
  const navigate = useNavigate();
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = async (file) => {
    setAnalysisResult(null);
    setError(null);
    setUploadedFile(file);
    setIsAnalyzing(true);

    const chunkSize = 10 * 1024 * 1024; // 10 mb
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

        await axios.post("http://127.0.0.1:8000/upload-chunk", formData);
        console.log(`Loaded chunk ${i + 1} of ${totalChunks}`);
      }

      const finalResponse = await axios.post("http://127.0.0.1:8000/analyze", {
        filename: file.name
      });

      setAnalysisResult(finalResponse.data);
      navigate('/analytics');

    } catch (err) {
      console.error(err);
      setError("Помилка завантаження або аналізу.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <AppShell navbar={{ width: 80, breakpoint: 'sm' }} padding="md" bg="#f8f9fa">
      <AppShell.Navbar p="0" style={{ borderRight: 0 }}>
        <Sidebar />
      </AppShell.Navbar>

      <AppShell.Main>
        {error && (
          <Alert variant="light" color="red" title="Помилка" icon={<IconAlertCircle />} mb="lg" withCloseButton onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Routes>
          <Route path="/" element={
            isAnalyzing ? (
              <AnalysisLoader />
            ) : (
              <div style={{ height: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <UploadArea onFileSelected={handleFileSelect} isLoading={isAnalyzing} />
              </div>
            )
          } />

          <Route path="/analytics" element={
            analysisResult ? (
              <StatsDashboard data={analysisResult} />
            ) : (
              <div style={{ textAlign: 'center', marginTop: '100px' }}>
                <Text c="dimmed">Будь ласка, спочатку завантажте відео для аналізу.</Text>
              </div>
            )
          } />
        </Routes>
      </AppShell.Main>
    </AppShell>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}