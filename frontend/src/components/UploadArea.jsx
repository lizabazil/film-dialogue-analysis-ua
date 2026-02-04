import { useRef } from 'react';
import { Text, Group, Button, rem, useMantineTheme } from '@mantine/core';
import { Dropzone, MIME_TYPES } from '@mantine/dropzone';
import { IconCloudUpload, IconX, IconDownload } from '@tabler/icons-react';

export function UploadArea({ onFileSelected }) {
  const theme = useMantineTheme();
  const openRef = useRef(null);

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
      <Text size="xl" fw={700} mb="lg">Upload Movie for Analysis</Text>

      <Dropzone
        openRef={openRef}
        onDrop={(files) => onFileSelected(files[0])} // Беремо перший файл
        onReject={(files) => console.log('rejected files', files)}
        maxSize={7 * 1024 ** 3} // allow files up to 7 GB
        accept={[MIME_TYPES.mp4, 'video/x-matroska', 'video/avi']}
        radius="lg"
        styles={{
            root: {
                border: '2px dashed #ced4da',
                backgroundColor: '#f8f9fa',
                '&:hover': { backgroundColor: '#f1f3f5' }
            }
        }}
      >
        <Group justify="center" gap="xl" style={{ minHeight: rem(220), pointerEvents: 'none' }}>
          <Dropzone.Accept>
            <IconDownload
              style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-blue-6)' }}
              stroke={1.5}
            />
          </Dropzone.Accept>
          <Dropzone.Reject>
            <IconX
              style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-red-6)' }}
              stroke={1.5}
            />
          </Dropzone.Reject>
          <Dropzone.Idle>
            <IconCloudUpload
              style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-dimmed)' }}
              stroke={1.5}
            />
          </Dropzone.Idle>

          <div>
            <Text size="xl" inline>
              Drag movie file here or click to select
            </Text>
            <Text size="sm" c="dimmed" inline mt={7}>
              Support: MP4, MKV, AVI (Max 5GB)
            </Text>
          </div>
        </Group>
      </Dropzone>

      <Button size="md" radius="xl" mt="xl" onClick={() => openRef.current?.()}>
        Select File from Computer
      </Button>
    </div>
  );
}