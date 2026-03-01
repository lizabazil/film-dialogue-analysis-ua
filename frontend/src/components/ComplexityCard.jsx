import { Paper, Text, Group, ThemeIcon, Stack, Badge, rem, SimpleGrid, Tooltip, ActionIcon } from '@mantine/core';
import { IconMan, IconWoman, IconCertificate, IconInfoCircle } from '@tabler/icons-react';

function InsightCard({ label, value, subtext, color, icon: Icon, isBechdel, points, tooltipLabel }) {
  const isPassed = value === true;
  const bgColor = `var(--mantine-color-${color}-light)`;
  const iconColor = `var(--mantine-color-${color}-filled)`;

  return (
    <Paper
      p="md"
      radius="24px"
      withBorder
      style={{
        backgroundColor: bgColor,
        borderColor: `var(--mantine-color-${color}-light-hover)`,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.03)',
        display: 'flex',
        alignItems: 'center',
        flex: 1,
        position: 'relative',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-3px)';
        e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.05)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.03)';
      }}
    >
      <Group wrap="nowrap" gap="md" style={{ width: '100%' }}>
        <ThemeIcon
          size={48}
          radius="xl"
          variant="white"
          color={color}
          style={{ boxShadow: '0 4px 10px rgba(0,0,0,0.05)' }}
        >
          <Icon size={26} style={{ color: iconColor }} />
        </ThemeIcon>

        <Stack gap={2} style={{ flex: 1 }}>
          <Group gap={4} align="center">
            <Text size="xs" c={color} fw={800} tt="uppercase" lts="0.8px" style={{ fontSize: '11px' }}>
              {label}
            </Text>

            {tooltipLabel && (
              <Tooltip
                label={tooltipLabel}
                multiline
                w={220}
                withArrow
                radius="md"
                transitionProps={{ transition: 'pop', duration: 200 }}
              >
                <ActionIcon variant="transparent" color={color} size="xs" radius="xl">
                  <IconInfoCircle size={14} stroke={2.5} />
                </ActionIcon>
              </Tooltip>
            )}
          </Group>

          {isBechdel ? (
            <Group gap="xs" align="center" mt={4}>
              <Badge
                color={isPassed ? 'green' : 'red'}
                variant="white"
                size="md"
                radius="sm"
                styles={{ root: { textTransform: 'none', fontWeight: 800 } }}
              >
                {isPassed ? 'Пройдено' : 'Не пройдено'}
              </Badge>
              <Text size="sm" fw={800} c="dark.3">
                Виконаних умов: {points} / 3
              </Text>
            </Group>
          ) : (
            <Stack gap={0}>
              <Group align="flex-baseline" gap={6}>
                <Text size="26px" fw={900} c="dark.6" style={{ lineHeight: 1.1 }}>
                  {(value || 0).toFixed(1)}
                </Text>
              </Group>
              <Text size="10px" c="dimmed" fw={600} style={{ marginTop: -2 }}>
                {subtext}
              </Text>
            </Stack>
          )}
        </Stack>
      </Group>
    </Paper>
  );
}

export function GenderInsights({ manMlu, womanMlu, bechdel }) {
  return (
    <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
      <InsightCard
        label="Красномовність (Чоловічі репліки)"
        value={manMlu}
        subtext="слів в середньому в репліці"
        color="indigo"
        icon={IconMan}
      />
      <InsightCard
        label="Красномовність (Жіночі репліки)"
        value={womanMlu}
        subtext="слів в середньому в репліці"
        color="pink"
        icon={IconWoman}
      />
      <InsightCard
        label="Тест Бекдел"
        isBechdel
        value={bechdel.passed_bechdel_test}
        points={bechdel.passed_points}
        color={bechdel.passed_bechdel_test ? 'teal' : 'orange'}
        icon={IconCertificate}
        tooltipLabel="Фільм проходить тест Бекдел, якщо: 1. Є принаймні дві жінки в сюжеті. 2. Які розмовляють між собою. 3. Тема розмови — не чоловік."
      />
    </SimpleGrid>
  );
}