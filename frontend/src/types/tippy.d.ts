declare global {
  interface Window {
    tippy: any; // We could make this more specific if needed
  }
  interface Element {
    _tippy?: any;
  }
}

export {}; 