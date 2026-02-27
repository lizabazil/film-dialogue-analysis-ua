import {
  Grid, Paper, Text, Group, rem, Code,
  Title, Stack, Box, ThemeIcon, SimpleGrid, Center, RingProgress, Divider, Progress
} from '@mantine/core';
import {
  IconClock, IconDatabase, IconGenderMale, IconGenderFemale, IconFileDescription, IconMicrophone,
    IconQuote
} from '@tabler/icons-react';
import { GeneralLexicon } from './GeneralLexicon';
import { KeywordBarChart } from './KeywordBarChart';
import { MetadataSmallCard} from "./MetadataSmallCard.jsx";
import { BubbleIndicator} from "./BubbleIndicator.jsx";
import { LegendDetail} from "./LegendDetail.jsx";
import { DonutLegendItem} from "./DonutLegendItem.jsx";
import { SpeechComplexity} from "./ComplexityCard.jsx";


export function StatsDashboard({ data }) {
  const rootData = data?.data || data;
  const { gender_stats: stats, metadata, speaker_lexicon } = rootData || {};

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

  const avgWordsPerReplicaWoman = stats?.avg_words_per_replica_woman || 0;
  const avgWordsPerReplicaMan = stats?.avg_words_per_replica_man || 0;

  const nouns = speaker_lexicon?.top_nouns_all_genders || [];
  const verbs = speaker_lexicon?.top_verbs_all_genders || [];
  const adjectives = speaker_lexicon?.top_adjectives_all_genders || [];


  const colors = {
    man: '#65489A',
    woman: '#B98793',
    silence: '#7FB9A3',
    manBarBase: '#2D4396',
    womanBarBase: '#E64980',
      allGendersBarBase: '#E8A755',
      manDonut: '#ABB2FA',
    womanDonut: '#F37D8B'
  };

  const getBubbleSize = (percent) => {
    const MIN_SIZE = 100;
    const MAX_SIZE = 180;
    return MIN_SIZE + (percent / 100) * (MAX_SIZE - MIN_SIZE);
  };

  return (
    <Box p="md" bg="#f8f9fa" minh="100vh">
      {/* 1. metadata */}
      <Paper radius="40px" p="xl" withBorder shadow="md" bg="white" mb="xl">
        <Stack gap="md">
          <Title order={3} fw={800} c="dark.4">Параметри файлу</Title>
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


      {/* boxes with average words per replica for each gender */}
      <Box mt="xl" mb="xl">
        <Title order={4} mb="md" ml="md" fw={700}>Аналіз довжини реплік</Title>
        <SpeechComplexity manMlu={avgWordsPerReplicaMan} womanMlu={avgWordsPerReplicaWoman} />
      </Box>

      {/* 3. most common words by gender */}
      <Grid gutter="xl" justify="center">
        <Grid.Col span={{ base: 12, md: 9 }}>
          <KeywordBarChart
            title="Найбільш вживані слова (Чоловіки)"
            keywords={speaker_lexicon?.top_man_lemmas}
            baseColor={colors.manBarBase}
            icon={IconGenderMale}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 9 }}>
          <KeywordBarChart
            title="Найбільш вживані слова (Жінки)"
            keywords={speaker_lexicon?.top_woman_lemmas}
            baseColor={colors.womanBarBase}
            icon={IconGenderFemale}
          />
        </Grid.Col>

           <Grid.Col span={{ base: 12, md: 9 }}>
          <KeywordBarChart
            title="Найбільш вживані слова"
            keywords={speaker_lexicon?.top_all_gender_lemmas}
            baseColor={colors.allGendersBarBase}
            icon={IconQuote}
          />
        </Grid.Col>
      </Grid>


        <Grid gutter="xl" mt="md" justify="center">
        <Grid.Col span={{ base: 12, md: 9 }}>
           <GeneralLexicon
              nouns={nouns}
              verbs={verbs}
              adjectives={adjectives}
           />
        </Grid.Col>
      </Grid>

      <Box mt={50} p="md">
  <Title order={5} mb="sm" c="dimmed">Debug Inspector:</Title>
  <Code block color="gray" style={{ maxHeight: '500px', overflow: 'auto' }}>
    {JSON.stringify(data, null, 2)}
  </Code>
</Box>
    </Box>
  );
}
