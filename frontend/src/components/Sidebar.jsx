import { Stack, Tooltip, UnstyledButton, rem } from '@mantine/core';
import { IconHome2, IconFileUpload, IconGraph, IconSettings } from '@tabler/icons-react';

function NavbarLink({ icon: Icon, label, active, onClick }) {
  return (
    <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
      <UnstyledButton
        onClick={onClick}
        style={{
          width: rem(50),
          height: rem(50),
          borderRadius: rem(10),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: active ? 'var(--mantine-color-violet-7)' : 'var(--mantine-color-gray-7)',
          backgroundColor: active ? 'var(--mantine-color-violet-0)' : 'transparent',
        }}
      >
        <Icon style={{ width: rem(24), height: rem(24) }} stroke={1.5} />
      </UnstyledButton>
    </Tooltip>
  );
}

export function Sidebar({ activeIndex, setActiveIndex }) {
  const links = [
    { icon: IconHome2, label: 'Home' },
    { icon: IconFileUpload, label: 'Upload' },
    { icon: IconGraph, label: 'Analytics' },
    { icon: IconSettings, label: 'Settings' },
  ];

  const items = links.map((link, index) => (
    <NavbarLink
      {...link}
      key={link.label}
      active={index === activeIndex}
      onClick={() => setActiveIndex(index)}
    />
  ));

  return (
    <nav style={{
      width: rem(80),
      height: '100vh',
      padding: '20px',
      borderRight: '1px solid #eee',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      backgroundColor: '#fff'
    }}>
      <Stack justify="center" gap={10}>
        {items}
      </Stack>
    </nav>
  );
}