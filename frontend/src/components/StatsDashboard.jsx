import {
  Grid, Paper, Text, Group, rem,
  Title, Stack, Box, ThemeIcon, SimpleGrid, Center
} from '@mantine/core';
import {
  IconClock, IconDatabase, IconMessage2,
  IconUserHeart, IconFileDescription, IconVolumeOff
} from '@tabler/icons-react';

export function StatsDashboard({ data }) {
  const { gender_stats: stats, metadata } = data || {};

  const womanMins = stats?.woman_time_minutes || 0;
  const manMins = stats?.man_time_minutes || 0;
  const totalDuration = metadata?.duration_minutes || 1;

  // percentages for each category
  const womanPercent = Math.round((womanMins / totalDuration) * 100);
  const manPercent = Math.round((manMins / totalDuration) * 100);
  const silenceMins = Math.max(0, totalDuration - womanMins - manMins);
  const silencePercent = Math.round((silenceMins / totalDuration) * 100);

  const MIN_SIZE = 100;  // for min size of the circle in the box
  const MAX_SIZE = 220;  // for max size of the circle in the box
  const getBubbleSize = (percent) => {
  return MIN_SIZE + (percent / 100) * (MAX_SIZE - MIN_SIZE);
};

  const manSize = getBubbleSize(manPercent);
  const womanSize = getBubbleSize(womanPercent);
  const silenceSize = getBubbleSize(silencePercent);

  const colors = {
    man: '#65489A',
    woman: '#B98793',
    silence: '#7FB9A3',
  };

  return (
    <Box p="md">
      {/* 1. metadata info */}
      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="lg" mb="30px">
        <MetadataSmallCard
          icon={IconFileDescription}
          title="Файл"
          value={metadata?.filename || 'Unknown'}
          color="blue"
          isTruncated
        />
        <MetadataSmallCard
          icon={IconClock}
          title="Тривалість"
          value={metadata?.formatted_duration || '00:00:00'}
          color="teal"
        />
        <MetadataSmallCard
          icon={IconDatabase}
          title="Розмір"
          value={`${metadata?.file_size_gb?.toFixed(2)} GB`}
          color="orange"
        />
      </SimpleGrid>

      {/* 2. box with three circles (woman, man and silence) */}
      <Paper radius="40px" p="xl" withBorder shadow="md" bg="white"
      maw={700} mx="left" w="100%" >
        <Stack gap="xl">
          <Group justify="space-between" px="md">
            <Stack gap={2}>
              <Title order={3} fw={800} c="dark.4">Аналіз голосової активності</Title>
              <Text size="sm" c="dimmed" fw={500}>Співвідношення голосів та фонового шуму</Text>
            </Stack>
          </Group>

          <Center py="lg">
            <Group gap={40} justify="center" wrap="wrap">

              <BubbleIndicator
                percent={manPercent}
                color={colors.man}
                label="Чоловіки"
                size={manSize}
              />

              <BubbleIndicator
                percent={womanPercent}
                color={colors.woman}
                label="Жінки"
                size={womanSize}
              />

              <BubbleIndicator
                percent={silencePercent}
                color={colors.silence}
                label="Тиша"
                size={silenceSize}
              />

            </Group>
          </Center>

          <SimpleGrid cols={3} mt="sm">
            <LegendDetail label="Чоловіча стать" value={`${manMins.toFixed(1)} хв`} color={colors.man} />
            <LegendDetail label="Жіноча стать" value={`${womanMins.toFixed(1)} хв`} color={colors.woman} />
            <LegendDetail label="Тиша" value={`${silenceMins.toFixed(1)} хв`} color={colors.silence} />
          </SimpleGrid>
        </Stack>
      </Paper>
    </Box>
  );
}


function BubbleIndicator({ percent, color, label, size }) {
  return (
    <Stack align="center" gap="xs">
      <Center
        w={size}
        h={size}
        style={{
          borderRadius: '50%',
          backgroundColor: `${color}33`,
          boxShadow: `0 8px 16px -4px ${color}40`,
          transition: 'transform 0.3s ease'
        }}
      >
        <Stack gap={0} align="center">
          <Text
            c={color}
            fw={900}
            size={rem(size / 4)}
            style={{ lineHeight: 1 }}
          >
            {percent}%
          </Text>
        </Stack>
      </Center>
      <Text fw={700} size="sm" c="dark.3">{label}</Text>
    </Stack>
  );
}

// for small metadata cards in the upper row of dashboard
function MetadataSmallCard({ icon: Icon, title, value, color, isTruncated }) {
  return (
    <Paper radius="24px" p="lg" withBorder shadow="xs">
      <Group gap="md" wrap="nowrap">
        <ThemeIcon size={44} radius="16px" variant="light" color={color}>
          <Icon size={24} />
        </ThemeIcon>

        <Stack gap={0} align="flex-start" style={{ flex: 1, overflow: 'hidden' }}>
          <Text size="xs" c="dimmed" fw={700} tt="uppercase" lts="1px">
            {title}
          </Text>
          <Text
            fw={800}
            size="md"
            truncate={isTruncated}
            title={isTruncated ? value : undefined}
            style={{ width: '100%' }}
          >
            {value}
          </Text>
        </Stack>
      </Group>
    </Paper>
  );
}


function LegendDetail({ label, value, color }) {
    return (
        <Stack gap={0} align="center">
            <Text size="xs" c="dimmed" fw={700} tt="uppercase">{label}</Text>
            <Text fw={800} c={color}>{value}</Text>
        </Stack>
    );
}