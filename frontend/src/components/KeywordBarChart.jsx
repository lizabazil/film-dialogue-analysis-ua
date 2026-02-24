import {Box, Group, Paper, Progress, Stack, Text, ThemeIcon, Title} from "@mantine/core";

export function KeywordBarChart({ title, keywords, baseColor, icon: Icon }) {
  const slicedKeywords = keywords?.slice(0, 10) || [];
  const maxCount = slicedKeywords.length > 0 ? Math.max(...slicedKeywords.map(k => k.count)) : 1;
  const totalItems = slicedKeywords.length;
  const textMainColor = "dark.7";

  return (
    <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" h="100%">
      <Stack gap="lg">
        <Group justify="space-between">
          <Group gap="xs">
            <ThemeIcon variant="light" color="gray" radius="xl" size="md">
               <Icon size={16} />
            </ThemeIcon>
            <Title order={3} fw={800} c="dark.4">{title}</Title>
          </Group>
        </Group>

        <Stack gap="md">
          {slicedKeywords.map((item, index) => {
            const lightenIntensity = (index / Math.max(1, totalItems - 1)) * 60;
            const rowColor = `color-mix(in srgb, ${baseColor}, white ${lightenIntensity}%)`;

            return (
              <Group key={index} gap="md" wrap="nowrap" align="center">
                <Box
                  w={8} h={8}
                  style={{ borderRadius: '50%', backgroundColor: rowColor, flexShrink: 0 }}
                />

                <Box style={{ flex: 1 }}>
                   <Progress
                      value={(item.count / maxCount) * 100}
                      color={rowColor}
                      size="xl"
                      radius="xl"
                      styles={{ section: { transition: 'width 1s ease' } }}
                   />
                </Box>

                <Text
                  size="sm"
                  fw={700}
                  w={130}
                  style={{
                    color: textMainColor,
                    whiteSpace: 'nowrap',
                    flexShrink: 0
                  }}
                >
                  {item.word}
                </Text>

                <Text
                  size="sm"
                  fw={800}
                  w={40}
                  ta="right"
                  style={{
                    color: textMainColor,
                    flexShrink: 0
                  }}
                >
                  {item.count}
                </Text>
              </Group>
            );
          })}
          {slicedKeywords.length === 0 && (
            <Text c="dimmed" ta="center" py="xl">Дані відсутні</Text>
          )}
        </Stack>
      </Stack>
    </Paper>
  );
}
