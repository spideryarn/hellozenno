import { describe, test, expect } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/svelte';
import EnhancedText from './EnhancedText.svelte';

describe('EnhancedText – punctuation and line-break preservation (structured mode)', () => {
  test('keeps period adjacent to linked word and renders double newline as <br><br>', () => {
    // Greek sample with a recognized word before a period and a paragraph break
    const text = 'Αυτό είναι μια λέξη.\n\nΚαι νέα παράγραφος';
    const token = 'λέξη';
    const start = text.indexOf(token);
    const end = start + token.length;

    const { container } = render(EnhancedText, {
      props: {
        text,
        recognizedWords: [
          {
            word: token,
            start,
            end,
            lemma: token,
            translations: []
          }
        ],
        target_language_code: 'el'
      }
    });

    // The linked word should render as an anchor with the correct text
    const link = container.querySelector('a.word-link');
    expect(link).toBeTruthy();
    expect(link?.textContent).toBe(token);

    // 1) The character immediately following the link (ignoring Svelte
    //    internal comment placeholders) should be a '.'
    function nextMeaningfulSibling(node: ChildNode | null): ChildNode | null {
      let n: ChildNode | null = node ? node.nextSibling : null;
      while (n) {
        if (n.nodeType === Node.COMMENT_NODE) {
          n = n.nextSibling;
          continue;
        }
        if (n.nodeType === Node.TEXT_NODE && (n.textContent ?? '').trim().length === 0) {
          n = n.nextSibling;
          continue;
        }
        return n;
      }
      return null;
    }

    const afterLink = nextMeaningfulSibling(link as unknown as ChildNode);
    expect(afterLink).toBeTruthy();
    expect(afterLink?.nodeType).toBe(Node.TEXT_NODE);
    expect(afterLink?.textContent?.trimStart().startsWith('.')).toBe(true);

    // 2) After the '.', we should see two consecutive <br> elements
    const afterPeriod = nextMeaningfulSibling(afterLink);
    expect(afterPeriod).toBeTruthy();
    // First <br>
    expect((afterPeriod as HTMLElement).nodeName).toBe('BR');
    const secondBr = nextMeaningfulSibling(afterPeriod);
    expect(secondBr).toBeTruthy();
    expect((secondBr as HTMLElement).nodeName).toBe('BR');

    // 3) No paragraph tags should be injected by the structured renderer
    //    (we rely on <br> only to preserve exact spacing/offsets)
    expect(container.querySelectorAll('p').length).toBe(0);
  });
});


