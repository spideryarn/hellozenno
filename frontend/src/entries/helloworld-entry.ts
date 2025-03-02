import '../styles/tailwind.css';
import HelloWorld from '../components/HelloWorld.svelte';

// Mount the Svelte component to the DOM
const target = document.getElementById('svelte-demo-component');
if (target) {
  new HelloWorld({
    target,
    props: {
      name: 'Hello Zenno',
    },
  });
}

// Add Tailwind classes to the Tailwind demo section
const tailwindDemo = document.getElementById('tailwind-demo-section');
if (tailwindDemo) {
  // Add a paragraph with Tailwind classes
  const paragraph = document.createElement('p');
  paragraph.className = 'tw-mt-4 tw-p-4 tw-bg-blue-100 tw-text-blue-800 tw-rounded-lg tw-border tw-border-blue-200';
  paragraph.textContent = 'This paragraph is styled with Tailwind CSS classes.';
  
  // Add some buttons with Tailwind classes
  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'tw-mt-4 tw-flex tw-gap-2';
  
  const primaryButton = document.createElement('button');
  primaryButton.className = 'tw-btn';
  primaryButton.textContent = 'Primary Button';
  
  const dangerButton = document.createElement('button');
  dangerButton.className = 'tw-btn tw-btn-danger';
  dangerButton.textContent = 'Danger Button';
  
  const successButton = document.createElement('button');
  successButton.className = 'tw-btn tw-btn-success';
  successButton.textContent = 'Success Button';
  
  buttonContainer.appendChild(primaryButton);
  buttonContainer.appendChild(dangerButton);
  buttonContainer.appendChild(successButton);
  
  // Append elements to the demo section
  tailwindDemo.appendChild(paragraph);
  tailwindDemo.appendChild(buttonContainer);
}

// Initialize Supabase demo section
// This will be implemented in a later stage
const supabaseDemo = document.getElementById('supabase-realtime-demo');
if (supabaseDemo) {
  const placeholder = document.createElement('p');
  placeholder.className = 'tw-p-4 tw-bg-gray-100 tw-text-gray-600 tw-rounded-lg';
  placeholder.textContent = 'Supabase realtime features will be implemented in a later stage.';
  
  supabaseDemo.appendChild(placeholder);
} 