import {Center, rem, Stack, Text} from "@mantine/core";

export function BubbleIndicator({ percent, color, label, size }) {
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
