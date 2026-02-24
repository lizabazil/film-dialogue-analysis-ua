import {useState} from "react";
import {Group, Paper, SegmentedControl, Stack, Title} from "@mantine/core";
import {IconTypography} from "@tabler/icons-react";
import { KeywordBarChart } from "./KeywordBarChart";

export function GeneralLexicon({ nouns, verbs, adjectives }) {
  const [section, setSection] = useState('nouns');
  const sectionColors = {
  nouns: '#5A67EA',
  verbs: '#EC9953',
  adjectives: '#9D66F8',
};

  const activeColor = sectionColors[section];

  const currentData = {
    nouns: nouns || [],
    verbs: verbs || [],
    adjectives: adjectives || []
  }[section];

  return (
    <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" mt="xl">
      <Stack gap="lg">
        <Group justify="space-between">
          <Group gap="sm">
            <Title order={3} fw={850} c="dark.5">Загальний лексикон фільму</Title>
          </Group>

          <SegmentedControl
            value={section}
            onChange={setSection}
            data={[
              { label: 'Іменники', value: 'nouns' },
              { label: 'Дієслова', value: 'verbs' },
              { label: 'Прикметники', value: 'adjectives' },
            ]}
            radius="xl"
            color={activeColor}
          />
        </Group>

        <KeywordBarChart
          title=""
          keywords={currentData}
          baseColor={activeColor}
          icon={IconTypography}
          isCompact
        />
      </Stack>
    </Paper>
  );
}