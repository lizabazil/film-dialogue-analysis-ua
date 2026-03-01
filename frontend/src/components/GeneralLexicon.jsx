import {Box, Group, Stack, Title, SimpleGrid, ThemeIcon, Text} from "@mantine/core";
import {IconTags, IconRun, IconSparkles} from "@tabler/icons-react";
import {KeywordBarChart} from "./KeywordBarChart";

export function GeneralLexicon({nouns, verbs, adjectives}) {
    const sectionColors = {
        nouns: '#5A67EA',
        verbs: '#EC9953',
        adjectives: '#9D66F8',
    };

    return (
        <Box mt="xl" mb="xl">
            <Group mb="md" ml="md" justify="space-between">
                <Stack gap={0}>
                    <Title order={4} fw={700}>Загальний лексикон фільму</Title>
                    <Text size="xs" c="dimmed">Розподіл за обраними частинами мови</Text>
                </Stack>
            </Group>

            <SimpleGrid cols={{base: 1, md: 3}} spacing="lg">
                <KeywordBarChart
                    title="Іменники"
                    keywords={nouns}
                    baseColor={sectionColors.nouns}
                    icon={IconTags}
                />
                <KeywordBarChart
                    title="Дієслова"
                    keywords={verbs}
                    baseColor={sectionColors.verbs}
                    icon={IconRun}
                />
                <KeywordBarChart
                    title="Прикметники"
                    keywords={adjectives}
                    baseColor={sectionColors.adjectives}
                    icon={IconSparkles}
                />
            </SimpleGrid>
        </Box>
    );
}