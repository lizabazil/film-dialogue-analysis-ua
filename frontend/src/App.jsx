import { useState } from 'react';
import { AppShell } from '@mantine/core';
import { Sidebar } from './components/Sidebar';
import { UploadArea } from './components/UploadArea';
import { StatsDashboard } from './components/StatsDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState(1); // 1 = Upload tab
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileSelect = (file) => {
    setUploadedFile(file);
    setIsAnalyzing(true);

    // here will be API call to backend for processing the video
    console.log("File selected:", file.name);

    // imitation of loading
    setTimeout(() => {
        setIsAnalyzing(false);
        setActiveTab(2); // switch to Analytics tab
    }, 2000);
  };

  return (
    <AppShell
      navbar={{ width: 80, breakpoint: 'sm' }}
      padding="md"
      style={{ background: '#f8f9fa' }} // light grey background
    >
      <AppShell.Navbar p="0" style={{ borderRight: 0 }}>
        <Sidebar activeIndex={activeTab} setActiveIndex={setActiveTab} />
      </AppShell.Navbar>

      <AppShell.Main>
        {activeTab === 1 && !uploadedFile && (
            <div style={{ height: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <UploadArea onFileSelected={handleFileSelect} />
            </div>
        )}

        {isAnalyzing && (
            <div style={{ textAlign: 'center', marginTop: 100 }}>
                <h2>Processing video...</h2>
                {/* TODO: spinner may be added (of the loading progress) */}
            </div>
        )}

        {activeTab === 2 && uploadedFile && (
            <StatsDashboard filename={uploadedFile.name} />
        )}
      </AppShell.Main>
    </AppShell>
  );
}