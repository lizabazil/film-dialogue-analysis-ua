import { Grid, Paper, Text, Group, RingProgress, rem, Code, Title } from '@mantine/core';
import { IconUser, IconDeviceTv, IconClock } from '@tabler/icons-react';

export function StatsDashboard({ filename, data }) {

  const StatCard = ({ title, value, icon: Icon, color, progress }) => (
    <Paper radius="lg" p="md" shadow="sm" withBorder style={{ height: '100%' }}>
      <Group justify="space-between">
        <div>
          <Text c="dimmed" size="xs" tt="uppercase" fw={700}>{title}</Text>
          <Text fw={700} size="xl">{value}</Text>
        </div>
        <Icon style={{ width: rem(28), height: rem(28) }} stroke={1.5} color={color} />
      </Group>

      {/* progress bar */}
      {progress && (
        <Group mt="md">
            <RingProgress
                size={80}
                roundCaps
                thickness={8}
                sections={[{ value: progress, color: color }]}
                label={<Text c={color} fw={700} ta="center" size="xs">{progress}%</Text>}
            />
             <Text size="xs" c="dimmed">Confidence</Text>
        </Group>
      )}
    </Paper>
  );

  return (
    <div>
      <Group mb="lg" justify="space-between">
        <div>
            <Title order={2}>Analysis Results</Title>
            <Text c="dimmed">File: {filename}</Text>
        </div>
      </Group>

      <Grid>
        {/* card 1: number of speakers */}
        <Grid.Col span={4}>
          <StatCard
            title="Total Speakers"
            value={data?.speakers || 0}
            icon={IconUser}
            color="violet"
          />
        </Grid.Col>

        {/* card 2: duration */}
        <Grid.Col span={4}>
          <StatCard
            title="Duration"
            value={data?.duration || "00:00"}
            icon={IconClock}
            color="teal"
          />
        </Grid.Col>

        {/* card 3: scenes detected */}
        <Grid.Col span={4}>
          <StatCard
            title="Scenes Detected"
            value={data?.scenes_detected || "Unknown"}
            icon={IconDeviceTv}
            color="orange"
          />
        </Grid.Col>
      </Grid>

      {/* TODO: only for debugging */}
      <Title order={4} mt="xl" mb="sm">Raw Backend Response:</Title>
      <Code block>
        {JSON.stringify(data, null, 2)}
      </Code>
    </div>
  );
}