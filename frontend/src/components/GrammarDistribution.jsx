import { Paper, Text, Group, Stack, Box, Tooltip, Divider, Title, rem } from '@mantine/core';

const POS_CONFIG = {
  NOUN: { label: 'Іменники' },
  VERB: { label: 'Дієслова'},
  PRON: { label: 'Займенники'},
  ADJ:  { label: 'Прикметники'},
  ADV:  { label: 'Прислівники' },
  PROPN: { label: 'Власні назви' },
  NUM: { label: 'Числівники' },
};

export function GrammarDistribution({ stats }) {
  const womanColor = '#F56945';
  const manColor = '#FEC8AC';

  const rawMax = Math.max(...stats.map(s => s.percentage), 5);
  const maxPercentage = Math.ceil(rawMax / 5) * 5 + 5;
  const chartHeight = 200;

  const partsOfSpeech = Object.keys(POS_CONFIG);
  const gridSteps = [0, 0.25, 0.5, 0.75, 1];

  return (
    <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" mb="xl">
      <Stack gap="xl">
        <Group justify="apart" align="flex-start" wrap="nowrap">
          <Stack gap={2}>
            <Title order={3} fw={800} c="dark.4">Граматичний профіль</Title>
            <Text size="sm" c="dimmed" fw={500}>Частота використання слів самостійних частин мови</Text>
          </Stack>

          <Group gap="xl" pt="xs">
            <Group gap={10}>
              <Box w={18} h={18} style={{ borderRadius: '6px', backgroundColor: womanColor }} />
              <Text size="md" fw={700} c="dark.3">Жінки</Text>
            </Group>
            <Group gap={10}>
              <Box w={18} h={18} style={{ borderRadius: '6px', backgroundColor: manColor }} />
              <Text size="md" fw={700} c="dark.3">Чоловіки</Text>
            </Group>
          </Group>
        </Group>

        <Box mt="xs" pl={45}>
          <Box style={{ position: 'relative', height: chartHeight }}>
            {gridSteps.map((step) => (
              <Box
                key={step}
                style={{
                  position: 'absolute',
                  bottom: `${step * 100}%`,
                  width: '100%',
                  zIndex: 0
                }}
              >
                <Text
                  size="xs"
                  c="dimmed"
                  fw={700}
                  style={{
                    position: 'absolute',
                    left: -45,
                    bottom: -8,
                    width: 40,
                    textAlign: 'right'
                  }}
                >
                  {Math.round(step * maxPercentage)}%
                </Text>
                <Divider
                  color="gray.1"
                  variant={step === 0 ? "solid" : "dashed"}
                  style={{ width: '100%' }}
                />
              </Box>
            ))}

            <Group
              justify="space-around"
              align="flex-end"
              w="100%"
              h="100%"
              gap="xl"
              wrap="nowrap"
              style={{ position: 'relative', zIndex: 1 }}
            >
              {partsOfSpeech.map((pos) => {
                const womanVal = stats.find(s => s.gender?.toLowerCase() === 'woman' && s.part_of_speech === pos)?.percentage || 0;
                const manVal = stats.find(s => s.gender?.toLowerCase() === 'man' && s.part_of_speech === pos)?.percentage || 0;

                return (
                  <Group key={pos} gap={6} align="flex-end" wrap="nowrap" style={{ flex: 1, justifyContent: 'center' }}>
                    <Tooltip label={`Жінки: ${womanVal.toFixed(1)}%`} withArrow radius="md">
                      <Box
                        style={{
                          width: rem(24),
                          height: `${(womanVal / maxPercentage) * chartHeight}px`,
                          backgroundColor: womanColor,
                          borderRadius: '8px 8px 2px 2px',
                          transition: 'height 1s ease',
                          cursor: 'pointer'
                        }}
                      />
                    </Tooltip>

                    <Tooltip label={`Чоловіки: ${manVal.toFixed(1)}%`} withArrow radius="md">
                      <Box
                        style={{
                          width: rem(24),
                          height: `${(manVal / maxPercentage) * chartHeight}px`,
                          backgroundColor: manColor,
                          borderRadius: '8px 8px 2px 2px',
                          transition: 'height 1s ease',
                          cursor: 'pointer'
                        }}
                      />
                    </Tooltip>
                  </Group>
                );
              })}
            </Group>
          </Box>

          <Group justify="space-around" w="100%" mt={16} gap="xl" wrap="nowrap">
            {partsOfSpeech.map((pos) => (
              <Box key={pos} style={{ flex: 1, textAlign: 'center' }}>
                <Text size="11px" fw={800} c="dark.3" tt="uppercase" style={{ letterSpacing: '0.3px' }}>
                  {POS_CONFIG[pos].label}
                </Text>
              </Box>
            ))}
          </Group>
        </Box>
      </Stack>
    </Paper>
  );
}