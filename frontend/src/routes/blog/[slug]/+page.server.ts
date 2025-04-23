import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { BlogPost } from '../+page.server';

// Mock data for a full blog post
// In a real implementation, this would come from a database or CMS
interface FullBlogPost extends BlogPost {
  content: string;
}

const blogPosts: Record<string, FullBlogPost> = {
  'hello-zenno-launch': {
    slug: 'hello-zenno-launch',
    title: 'Introducing Hello Zenno',
    excerpt: 'Today we\'re proud to unveil Hello Zenno, a new approach to intermediate language learning that helps you break through vocabulary plateaus.',
    date: '2024-04-23',
    author: 'Greg',
    coverImage: '/img/marketing/word_highlighting.png',
    content: `
## Breaking through the intermediate plateau

Learning a language can feel like climbing a mountain. The initial ascent is steep but clear - learn basic greetings, master simple present tense, memorize 500 common words. But many learners reach what linguists call the "intermediate plateau" - where progress slows dramatically.

It\'s not that you\'ve stopped learning. It\'s that you need *thousands* more words before native content feels comfortable. And worse - listening comprehension often lags far behind reading ability.

## The Hello Zenno approach

Hello Zenno takes a different approach:

1. **Import any text you care about** - articles, stories, or transcripts that genuinely interest you
2. **Highlight tricky words with AI assistance** - we predict which words might trip you up
3. **Generate rich dictionary entries on demand** - including etymology, similar words, and example usage
4. **Train your ears with audio flashcards** - hear the same words in new contexts

The most powerful feature is our **enhanced text view** where you can hover over any word to instantly see its meaning without disrupting your reading flow.

## Try it today

Hello Zenno is completely free to use. Sign up and import your first text to experience a new way of tackling intermediate language learning.

[Get started with Hello Zenno](/languages)
`
  }
};

export const load: PageServerLoad = async ({ params }) => {
  const { slug } = params;
  
  const post = blogPosts[slug];
  
  if (!post) {
    throw error(404, 'Blog post not found');
  }
  
  return {
    post
  };
};