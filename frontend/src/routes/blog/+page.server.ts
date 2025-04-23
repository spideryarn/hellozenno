import type { PageServerLoad } from './$types';

// Mock data for blog posts
// In a real implementation, this would come from a database or API
export interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  author: string;
  coverImage?: string;
}

const blogPosts: BlogPost[] = [
  {
    slug: 'hello-zenno-launch',
    title: 'Introducing Hello Zenno',
    excerpt: 'Today we\'re proud to unveil Hello Zenno, a new approach to intermediate language learning that helps you break through vocabulary plateaus.',
    date: '2024-04-23',
    author: 'Greg',
    coverImage: '/img/marketing/word_highlighting.png'
  }
];

export const load: PageServerLoad = async () => {
  // Sort posts by date (newest first)
  const sortedPosts = [...blogPosts].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  );
  
  return {
    posts: sortedPosts
  };
};