import {
  Grid, Paper, Text, Group, rem,
  Title, Stack, Box, ThemeIcon, SimpleGrid, Center, RingProgress, Divider
} from '@mantine/core';
import {
  IconClock, IconDatabase, IconMessage2,
  IconUserHeart, IconFileDescription, IconVolumeOff, IconChartDonut, IconMicrophone
} from '@tabler/icons-react';

export function StatsDashboard({ data }) {
  const { gender_stats: stats, metadata } = data || {};

  const womanMins = stats?.woman_time_minutes || 0;
  const manMins = stats?.man_time_minutes || 0;
  const womanReplicas = stats?.woman_replicas || 0;
  const manReplicas = stats?.man_replicas || 0;
  const totalReplicas = womanReplicas + manReplicas;
  const totalDurationMinutes = metadata?.duration_minutes || 1;

  const womanPercent = Math.round((womanMins / totalDurationMinutes) * 100);
  const manPercent = Math.round((manMins / totalDurationMinutes) * 100);
  const silenceMins = Math.max(0, totalDurationMinutes - womanMins - manMins);
  const silencePercent = Math.round((silenceMins / totalDurationMinutes) * 100);

  const manRepPercent = totalReplicas > 0 ? Math.round((manReplicas / totalReplicas) * 100) : 0;
  const womanRepPercent = totalReplicas > 0 ? Math.round((womanReplicas / totalReplicas) * 100) : 0;

  const getBubbleSize = (percent) => {
    const MIN_SIZE = 100;
    const MAX_SIZE = 180;
    return MIN_SIZE + (percent / 100) * (MAX_SIZE - MIN_SIZE);
  };

  const colors = {
    man: '#65489A',
    woman: '#B98793',
    silence: '#7FB9A3',
    manDonut: '#ABB2FA',
    womanDonut: '#F37D8B'
  };

  return (
    <Box p="md" bg="#f8f9fa" minh="100vh">
      <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" mb="xl">
        <Stack gap="md">
          <Stack gap={2} mb="xs">
            <Title order={3} fw={800} c="dark.4">Параметри файлу</Title>
            <Text size="sm" c="dimmed" fw={500}>Загальна інформація про медіафайл</Text>
          </Stack>
          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm">
            <MetadataSmallCard icon={IconFileDescription} title="Файл" value={metadata?.filename || 'Unknown'} color="blue" isTruncated />
            <MetadataSmallCard icon={IconClock} title="Тривалість" value={metadata?.formatted_duration || '00:00:00'} color="teal" />
            <MetadataSmallCard icon={IconDatabase} title="Розмір" value={`${metadata?.file_size_gb?.toFixed(2)} GB`} color="orange" />
          </SimpleGrid>
        </Stack>
      </Paper>

      <Grid gutter="xl">
        {/* left box */}
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" h="100%">
            <Stack gap="xl" h="100%" justify="space-between">
              <Stack gap={2}>
                <Title order={3} fw={800} c="dark.4">Розподіл часу мовлення за статями</Title>
                <Text size="sm" c="dimmed" fw={500}>Співвідношення голосів та фонового шуму</Text>
              </Stack>

              <Center py="lg">
                <Group gap={30} justify="center" wrap="wrap">
                  <BubbleIndicator percent={manPercent} color={colors.man} label="Чоловіки" size={getBubbleSize(manPercent)} />
                  <BubbleIndicator percent={womanPercent} color={colors.woman} label="Жінки" size={getBubbleSize(womanPercent)} />
                  <BubbleIndicator percent={silencePercent} color={colors.silence} label="Тиша" size={getBubbleSize(silencePercent)} />
                </Group>
              </Center>

              <SimpleGrid cols={3} pt="md">
                <LegendDetail label="Чоловіча стать" value={`${manMins.toFixed(1)} хв`} color={colors.man} />
                <LegendDetail label="Жіноча стать" value={`${womanMins.toFixed(1)} хв`} color={colors.woman} />
                <LegendDetail label="Тиша" value={`${silenceMins.toFixed(1)} хв`} color={colors.silence} />
              </SimpleGrid>
            </Stack>
          </Paper>
        </Grid.Col>

        {/* right box */}
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" h="100%">
            <Stack gap="xl">
              <Stack gap={2}>
                <Title order={3} fw={800} c="dark.4">Розподіл реплік за статями</Title>
                <Text size="sm" c="dimmed" fw={500}>Аналіз за кількістю фраз</Text>
              </Stack>

              <Center py="xl">
                <Group gap="xl" wrap="nowrap">
                  <RingProgress
                    size={160}
                    thickness={16}
                    roundCaps
                    sections={[
                      { value: manRepPercent, color: colors.manDonut },
                      { value: womanRepPercent, color: colors.womanDonut },
                    ]}
                    label={
                      <Center>
                        <ThemeIcon color="gray.1" variant="light" radius="xl" size="xl">
                            <IconMicrophone
                              style={{ width: rem(22), height: rem(22) }}
                              color="gray"
                            />
                        </ThemeIcon>
                      </Center>
                    }
                  />
                  <Stack gap="xs">
                    <DonutLegendItem color={colors.manDonut} label="Чоловіки" value={manReplicas} percent={manRepPercent} />
                    <DonutLegendItem color={colors.womanDonut} label="Жінки" value={womanReplicas} percent={womanRepPercent} />
                    <Divider my="xs" />
                    <Text size="15px" c="dimmed" fw={700}>Всього: {totalReplicas} реплік</Text>
                  </Stack>
                </Group>
              </Center>

              <Paper withBorder radius="lg" p="md" bg="gray.0">
                 <Text size="sm" fw={600} ta="center">Стать із більшої кількістю реплік: {manReplicas > womanReplicas ? "Чоловіча" : "Жіноча"}</Text>
              </Paper>
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

      {/* for debug */}
      <Box mt="xl" p="md" style={{ opacity: 0.5 }}>
        <Text size="xs" family="monospace">{JSON.stringify({ data })}</Text>
      </Box>
    </Box>
  );
}


function DonutLegendItem({ color, label, value, percent }) {
  return (
    <Group justify="space-between" wrap="nowrap" gap="xl">
      <Group gap="xs">
        <Box w={8} h={8} style={{ borderRadius: '50%', backgroundColor: color }} />
        <Text size="sm" fw={700} c="dark.3">{label}</Text>
      </Group>
      <Stack gap={0} align="flex-end">
        <Text size="sm" fw={800}>{percent}%</Text>
        <Text size="15px" c="dimmed">{value} шт.</Text>
      </Stack>
    </Group>
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
  const pastelMap = {
    blue: { bg: '#F3F0FF', icon: '#A197FF' },
    teal: { bg: '#EBFBEE', icon: '#66D19E' },
    orange: { bg: '#FFF9DB', icon: '#FFD56D' },
    pink: { bg: '#FFF0F6', icon: '#FF8BA7' },
  };

  const theme = pastelMap[color] || pastelMap.blue;

  return (
    <Paper
      radius="18px"
      p="md"
      shadow="none"
      style={{
        backgroundColor: theme.bg,
        border: 'none',
      }}
    >
      <Group gap="sm" wrap="nowrap">
        <ThemeIcon
          size={34}
          radius="50%"
          style={{
            backgroundColor: theme.icon,
            color: 'white',
          }}
        >
          <Icon size={18} />
        </ThemeIcon>

        <Stack gap={0} style={{ flex: 1, overflow: 'hidden' }}>
          <Text
            fw={900}
            size="md"
            c="dark.7"
            truncate={isTruncated}
            style={{ lineHeight: 1.2 }}
          >
            {value}
          </Text>
          <Text
            size="10px"
            c="dimmed"
            fw={700}
            tt="uppercase"
            lts="0.5px"
            style={{ opacity: 0.8 }}
          >
            {title}
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