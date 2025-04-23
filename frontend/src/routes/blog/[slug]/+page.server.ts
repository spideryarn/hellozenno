import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { BlogPost } from '../+page.server';

// Mock data for a full blog post
// In a real implementation, this would come from a database or CMS
interface FullBlogPost extends BlogPost {
  // No content field - we're using hardcoded HTML instead
}

const blogPosts: Record<string, FullBlogPost> = {
  'hello-zenno-launch': {
    slug: 'hello-zenno-launch',
    title: 'Introducing Hello Zenno',
    excerpt: 'Today we\'re proud to unveil Hello Zenno, a new approach to intermediate language learning that helps you break through vocabulary plateaus.',
    date: '2024-04-23',
    author: 'Greg',
    coverImage: '/img/marketing/word_highlighting.png'
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