import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { theme } from '../src/theme';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: theme.bg2 },
          headerTintColor: theme.text,
          headerTitleStyle: { color: theme.text },
          contentStyle: { backgroundColor: theme.bg },
        }}
      >
        <Stack.Screen name="index" options={{ title: 'Once Human Guide' }} />
        <Stack.Screen name="step/[id]" options={{ title: 'Krok' }} />
      </Stack>
    </>
  );
}
