import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import React from 'react';

type Lang = 'en' | 'ko';

interface LangContextValue {
  lang: Lang;
  toggle: () => void;
}

const LangContext = createContext<LangContextValue>({ lang: 'en', toggle: () => {} });

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(
    () => (localStorage.getItem('bmad-lang') as Lang) || 'ko',
  );

  const toggle = useCallback(() => {
    setLang((prev) => {
      const next = prev === 'en' ? 'ko' : 'en';
      localStorage.setItem('bmad-lang', next);
      return next;
    });
  }, []);

  return React.createElement(LangContext.Provider, { value: { lang, toggle } }, children);
}

export function useLang() {
  return useContext(LangContext);
}
