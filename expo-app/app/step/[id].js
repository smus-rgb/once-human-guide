import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';
import { allSteps, loadGuide } from '../../src/guide';
import { theme } from '../../src/theme';

function Block({ label, children }) {
  return (
    <View style={styles.block}>
      <Text style={styles.kind}>{label}</Text>
      {children}
    </View>
  );
}

export default function StepScreen() {
  const { id } = useLocalSearchParams();
  const [step, setStep] = useState(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    let alive = true;
    loadGuide().then(({ doc }) => {
      if (!alive) return;
      const found = allSteps(doc).find((s) => s.id === id);
      if (found) setStep(found);
      else setMissing(true);
    });
    return () => {
      alive = false;
    };
  }, [id]);

  if (missing) {
    return (
      <View style={styles.screen}>
        <Stack.Screen options={{ title: 'Nenalezeno' }} />
        <Text style={styles.muted}>Krok {String(id)} v guide.json není.</Text>
      </View>
    );
  }

  if (!step) {
    return (
      <View style={styles.screen}>
        <Text style={styles.muted}>Načítám krok…</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Stack.Screen options={{ title: step.title }} />
      <Text style={styles.kicker}>{step._pathTitle}</Text>
      <Text style={styles.h1}>{step.title}</Text>
      {step.time_estimate ? <Text style={styles.muted}>Čas: {step.time_estimate}</Text> : null}
      {step.goal ? (
        <Block label="Cíl">
          <Text style={styles.body}>{step.goal}</Text>
        </Block>
      ) : null}
      {step.why ? (
        <Block label="Proč">
          <Text style={styles.body}>{step.why}</Text>
        </Block>
      ) : null}
      {step.actions && step.actions.length ? (
        <Block label="Postup">
          {step.actions.map((a, i) => (
            <Text key={i} style={styles.body}>
              {i + 1}. {a}
            </Text>
          ))}
        </Block>
      ) : null}
      {step.tips && step.tips.length ? (
        <View style={styles.card}>
          <Text style={styles.kind}>Tip</Text>
          {step.tips.map((t, i) => (
            <Text key={i} style={styles.body}>
              {t}
            </Text>
          ))}
        </View>
      ) : null}
      {step.links && step.links.length ? (
        <Block label="V databázi">
          <View style={styles.chipRow}>
            {step.links.map((l) => (
              <Text key={l.table + l.id} style={styles.chip}>
                {l.label || l.id}
              </Text>
            ))}
          </View>
        </Block>
      ) : null}
      {(step.source_refs || []).length || step.verified_at ? (
        <Text style={styles.muted}>
          Zdroj: {(step.source_refs || []).join(', ')}
          {step.verified_at ? ` · ověřeno ${step.verified_at}` : ''}
        </Text>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: theme.bg, padding: 16 },
  content: { paddingBottom: 40, gap: 6 },
  kicker: { color: theme.acc, fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' },
  h1: { color: theme.text, fontSize: 20, fontWeight: '700' },
  muted: { color: theme.muted, fontSize: 12 },
  block: { marginTop: 10 },
  card: {
    marginTop: 12,
    backgroundColor: theme.bg2,
    borderWidth: 1,
    borderColor: theme.line,
    borderRadius: 12,
    padding: 12,
    gap: 4,
  },
  kind: { color: theme.acc, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 4 },
  body: { color: theme.text, fontSize: 14, lineHeight: 20, marginTop: 2 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  chip: {
    color: theme.text,
    backgroundColor: theme.bg3,
    borderWidth: 1,
    borderColor: theme.line,
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    fontSize: 12,
  },
});
