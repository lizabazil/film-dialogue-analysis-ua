import { Grid, Paper, Text, Group, RingProgress, rem } from '@mantine/core';
import { IconUser, IconDeviceTv, IconClock } from '@tabler/icons-react';

export function StatsDashboard({ filename }) {

  // component for individual statistic card
  const StatCard = ({ title, value, icon: Icon, color, progress }) => (
    <Paper radius="lg" p="md" shadow="sm" withBorder style={{ height: '100%' }}>
      <Group justify="space-between">
        <div>
          <Text c="dimmed" size="xs" tt="uppercase" fw={700}>{title}</Text>
          <Text fw={700} size="xl">{value}</Text>
        </div>
        <Icon style={{ width: rem(28), height: rem(28) }} stroke={1.5} color={color} />
      </Group>

      {/* circle progress */}
      {/*<Group mt="md">*/}
      {/*   <RingProgress*/}
      {/*      size={80}*/}
      {/*      roundCaps*/}
      {/*      thickness={8}*/}
      {/*      sections={[{ value: progress, color: color }]}*/}
      {/*      label={*/}
      {/*        <Text c={color} fw={700} ta="center" size="xs">*/}
      {/*          {progress}%*/}
      {/*        </Text>*/}
      {/*      }*/}
      {/*    />*/}
      {/*    <Text size="xs" c="dimmed" style={{ flex: 1 }}>*/}
      {/*      Analysis confidence score*/}
      {/*    </Text>*/}
      {/*</Group>*/}
    </Paper>
  );

  return (
    <div>
      <Text size="h2" mb="lg">Analysis Results: {filename}</Text>
      <Grid>
        <Grid.Col span={4}>
          <StatCard title="All replicas" value="122" icon={IconUser} color="violet" progress={85} />
        </Grid.Col>
        <Grid.Col span={4}>
          <StatCard title="Total Duration" value="1h 45m" icon={IconClock} color="teal" progress={100} />
        </Grid.Col>
        <Grid.Col span={4}>
          <StatCard title="Dialogue Scenes" value="34" icon={IconDeviceTv} color="orange" progress={60} />
        </Grid.Col>
        {/* TODO: later will be graphs, plots */}
      </Grid>
    </div>
  );
}