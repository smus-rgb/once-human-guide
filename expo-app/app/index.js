import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useRouter } from 'expo-router';
import { allSteps, loadGuide, searchGuide } from '../src/guide';
import { theme } from '../src/theme';

export default function GuideHome() {
  const router = useRouter();
  const [state, setState] = useState({ loading: true, doc: null, source: 'local' });
  const [query, setQuery] = useState('');

  useEffect(() => {
    let alive = true;
    loadGuide().then(({ doc, source }) => {
      if (alive) setState({ loading: false, doc, source });
    });
    return () => {
      alive = false;
    };
  }, []);

  const results = useMemo(
    () => (state.doc ? searchGuide(state.doc, query) : { steps: [], faq: [], glossary: [] }),
    [state.doc, query]
  );
  const paths = (state.doc && state.doc.paths) || [];
  const steps = state.doc ? allSteps(state.doc) : [];
  const searching = query.trim().length > 0;

  if (state.loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.acc} />
        <Text style={styles.muted}>Načítám průvodce…</Text>
      </View>
    );
  }

  const rows = searching
    ? [
        ...results.steps.map((s) => ({ key: 'step-' + s.id, kind: s._pathTitle, title: s.title, sub: s.goal, id: s.id })),
        ...results.faq.map((f) => ({ key: 'faq-' + f.id, kind: 'FAQ', title: f.q, sub: f.a })),
        ...results.glossary.map((g) => ({ key: 'term-' + g.term, kind: 'Pojem', title: g.term, sub: g.definition })),
      ]
    : paths.flatMap((p) =>
        (p.steps || []).map((s) => ({ key: p.id + '-' + s.id, kind: p.title, title: s.title, sub: s.goal, id: s.id }))
      );

  return (
    <View style={styles.screen}>
      <Text style={styles.kicker}>Guide · {state.source}</Text>
      <Text style={styles.h1}>Průvodce hráčem</Text>
      <Text style={styles.muted}>
        {paths.length} cest · {steps.length} kroků
      </Text>
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder="Hledat — název nebo klíčová slova…"
        placeholderTextColor={theme.muted}
        style={styles.input}
        autoCorrect={false}
        autoCapitalize="none"
        returnKeyType="search"
      />
      {searching ? (
        <Text style={styles.muted}>
          {results.steps.length} kroků · {results.faq.length} FAQ · {results.glossary.length} pojmů
        </Text>
      ) : null}
      <FlatList
        data={rows}
        keyExtractor={(item) => item.key}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={styles.muted}>
            {searching ? 'Nic nenalezeno — zkus jiné klíčové slovo.' : 'guide.json zatím nemá žádné kroky.'}
          </Text>
        }
        renderItem={({ item }) => (
          <Pressable
            style={styles.row}
            disabled={!item.id}
            onPress={() => item.id && router.push(`/step/${item.id}`)}
          >
            <View style={styles.rowBody}>
              <Text style={styles.kind}>{item.kind}</Text>
              <Text style={styles.title}>{item.title}</Text>
              <Text style={styles.muted} numberOfLines={2}>
                {item.sub}
              </Text>
            </View>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: theme.bg, padding: 16 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: theme.bg, gap: 8 },
  kicker: { color: theme.acc, fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' },
  h1: { color: theme.text, fontSize: 22, fontWeight: '700', marginTop: 2 },
  muted: { color: theme.muted, fontSize: 12 },
  input: {
    marginTop: 12,
    marginBottom: 10,
    backgroundColor: theme.bg3,
    borderWidth: 1,
    borderColor: theme.line,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: theme.text,
    minHeight: 44,
  },
  list: { paddingBottom: 32, gap: 8 },
  row: {
    backgroundColor: theme.bg2,
    borderWidth: 1,
    borderColor: theme.line,
    borderRadius: 12,
    padding: 12,
    minHeight: 44,
  },
  rowBody: { flex: 1 },
  kind: { color: theme.acc, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.6 },
  title: { color: theme.text, fontSize: 15, fontWeight: '600', marginVertical: 2 },
});
