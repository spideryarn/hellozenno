<script lang="ts">
  import { onMount } from 'svelte';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import TableOfContents from '$lib/components/TableOfContents.svelte';
  import { SITE_NAME, CONTACT_EMAIL, GITHUB_ISSUES_URL } from '$lib/config';
  import ArrowUp from 'phosphor-svelte/lib/ArrowUp';
  import ContactButton from '$lib/components/ContactButton.svelte';
  import GithubIssueButton from '$lib/components/GithubIssueButton.svelte';
  
  onMount(() => {
    // Handle any initialization on mount if needed
  });
  
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Update URL to remove the fragment
    history.replaceState(null, document.title, window.location.pathname + window.location.search);
  }
  
  // Privacy Policy data grouped by categories
  const privacyCategories = [
    {
      id: "introduction",
      title: "Introduction",
      faqs: [
        {
          id: "welcome",
          question: "About this Privacy Policy",
          answer: `
            This Privacy Policy explains how Hello Zenno collects, uses, and protects your information when 
            you use our application and services.
            <br><br>
            <strong>Please note:</strong> Hello Zenno is currently in its earliest stages of development. 
            This policy is subject to change as the site evolves. We'll make reasonable efforts to notify 
            users of significant changes.
          `
        },
        {
          id: "acceptance",
          question: "Acceptance of Policy",
          answer: `
            By using Hello Zenno, you consent to the collection and use of information as described in this policy.
            If you do not agree with our policies, please do not use our services.
          `
        }
      ]
    },
    {
      id: "collection",
      title: "Information We Collect",
      faqs: [
        {
          id: "account-info",
          question: "Account Information",
          answer: `
            When you create an account, we collect:
            <ul>
              <li>Username</li>
              <li>Email address</li>
              <li>Password (securely hashed)</li>
            </ul>
            If you choose to sign in with Google (future feature), we may receive additional profile information from your Google account.
          `
        },
        {
          id: "content",
          question: "User-Uploaded Content",
          answer: `
            We collect content that you voluntarily provide, including:
            <ul>
              <li>Text that you directly paste/type</li>
              <li>URLs you provide for downloading content</li>
              <li>MP3 audio files you upload</li>
              <li>Images you upload (e.g., photographs of books or magazine text)</li>
            </ul>
            <strong>Important:</strong> Currently, all uploaded content is visible to other users. 
            We plan to add private content options in the future.
          `
        },
        {
          id: "technical-data",
          question: "Technical and Usage Data",
          answer: `
            We automatically collect certain information when you use Hello Zenno:
            <ul>
              <li>IP addresses</li>
              <li>Browser type and version</li>
              <li>Pages visited and features used</li>
              <li>Time and date of visits</li>
              <li>Analytics data via Google Analytics</li>
            </ul>
            This information helps us improve our services and user experience.
          `
        },
        {
          id: "cookies",
          question: "Cookies and Similar Technologies",
          answer: `
            Hello Zenno uses cookies and similar technologies for:
            <ul>
              <li>Authentication (maintaining login status)</li>
              <li>Site functionality (remembering preferences)</li>
              <li>Analytics (understanding usage patterns)</li>
            </ul>
            You can configure your browser to refuse cookies, but this may limit your ability to use certain features.
          `
        }
      ]
    },
    {
      id: "usage",
      title: "How We Use Your Information",
      faqs: [
        {
          id: "service-provision",
          question: "Providing and Improving Services",
          answer: `
            We use your information to:
            <ul>
              <li>Operate and maintain Hello Zenno</li>
              <li>Process and generate AI-enhanced content</li>
              <li>Generate audio from text</li>
              <li>Improve our services based on usage patterns</li>
              <li>Respond to your requests and support needs</li>
            </ul>
          `
        },
        {
          id: "ai-processing",
          question: "AI Processing of Data",
          answer: `
            Hello Zenno uses several AI services to enhance language learning:
            <ul>
              <li>Anthropic Claude: For generating dictionary entries and processing text</li>
              <li>Eleven Labs: For generating audio from text</li>
              <li>Potentially other AI providers for specific language tasks</li>
            </ul>
            Content you upload or create may be sent to these services for processing. This is solely for 
            providing our core functionality - data is not shared for marketing or other secondary purposes.
          `
        }
      ]
    },
    {
      id: "sharing",
      title: "Information Sharing",
      faqs: [
        {
          id: "third-parties",
          question: "Third-Party Service Providers",
          answer: `
            We share information with trusted service providers who help us operate Hello Zenno:
            <ul>
              <li>Supabase for authentication and database services</li>
              <li>Vercel for hosting</li>
              <li>Google Analytics for usage data</li>
              <li>AI model providers (Anthropic, Eleven Labs, etc.)</li>
            </ul>
            These providers are bound by contractual obligations to keep personal information confidential 
            and use it only for the purposes for which we disclose it to them.
          `
        },
        {
          id: "user-uploaded",
          question: "Visibility of User-Uploaded Content",
          answer: `
            <strong>Important:</strong> Currently, all content uploaded to Hello Zenno is visible to other users. 
            There is no mechanism to mark content as private.
            <br><br>
            Only upload content that you're comfortable sharing with others. We recommend using public domain 
            material or content you have rights to share.
          `
        },
        {
          id: "no-selling",
          question: "No Selling of Data",
          answer: `
            We do not sell your personal information to third parties. User data is used solely for providing 
            and improving Hello Zenno's services.
          `
        },
        {
          id: "legal-compliance",
          question: "Legal Requirements",
          answer: `
            We may disclose your information if required by law, regulation, legal process, or governmental request.
          `
        }
      ]
    },
    {
      id: "retention",
      title: "Data Retention & Deletion",
      faqs: [
        {
          id: "retention-period",
          question: "How Long We Keep Information",
          answer: `
            We retain different types of data for different periods:
            <ul>
              <li><strong>Public Content:</strong> All public uploaded texts and AI-generated content is retained indefinitely</li>
              <li><strong>User-Specific Data:</strong> Retained until you delete your account or request deletion</li>
              <li><strong>Technical Data:</strong> Typically retained for analytics purposes for a limited period</li>
            </ul>
          `
        },
        {
          id: "account-deletion",
          question: "Account Deletion",
          answer: `
            You can request account deletion by contacting ${CONTACT_EMAIL}. Upon deletion, we will remove:
            <ul>
              <li>Personal identifiable information (email address)</li>
              <li>User preferences (e.g., target language selection)</li>
              <li>User-specific data such as "ignored words" lists</li>
            </ul>
            However, the following will be retained:
            <ul>
              <li>AI-generated content (dictionary entries, sentences, etc.)</li>
              <li>Public source files and their derivatives</li>
              <li>Anonymous usage data previously sent to analytics services</li>
            </ul>
          `
        }
      ]
    },
    {
      id: "security",
      title: "Data Security",
      faqs: [
        {
          id: "security-measures",
          question: "How We Protect Your Information",
          answer: `
            We implement reasonable security measures to protect your information:
            <ul>
              <li>Authentication security via Supabase with passwords securely hashed using bcrypt</li>
              <li>JWT (JSON Web Tokens) for secure session management</li>
              <li>HTTPS encryption for all data transmitted through our site</li>
              <li>Database security through Supabase's security practices</li>
              <li>Data encryption at rest with AES-256 through Supabase</li>
            </ul>
            While we strive to protect your information, no method of transmission over the Internet or 
            electronic storage is 100% secure. We cannot guarantee absolute security.
          `
        }
      ]
    },
    {
      id: "rights",
      title: "Your Rights & Choices",
      faqs: [
        {
          id: "access-correct",
          question: "Access and Correction",
          answer: `
            You can access and update most of your information through your account settings. 
            If you need help accessing, correcting, or deleting information that cannot be accessed 
            through your account, please contact ${CONTACT_EMAIL}.
          `
        },
        {
          id: "opt-out",
          question: "Opt-Out Options",
          answer: `
            <ul>
              <li><strong>Analytics:</strong> You can opt out of Google Analytics by installing the Google Analytics Opt-out Browser Add-on</li>
              <li><strong>Cookies:</strong> You can set your browser to refuse cookies, though this may affect functionality</li>
              <li><strong>Marketing Communications:</strong> You can opt out of marketing emails by using the unsubscribe link in those emails</li>
            </ul>
          `
        }
      ]
    },
    {
      id: "children",
      title: "Children's Privacy",
      faqs: [
        {
          id: "age-restriction",
          question: "Minimum Age Requirement",
          answer: `
            Hello Zenno is intended for users who are at least 13 years of age. We do not knowingly collect 
            personal information from children under 13. If we learn we have collected personal information 
            from a child under 13, we will delete that information.
            <br><br>
            If you believe we might have any information from or about a child under 13, please contact ${CONTACT_EMAIL}.
          `
        }
      ]
    },
    {
      id: "changes",
      title: "Changes & Contact",
      faqs: [
        {
          id: "changes-to-privacy",
          question: "Changes to this Privacy Policy",
          answer: `
            We may update this Privacy Policy from time to time. We will notify users of significant changes 
            by posting a notice on our website or sending an email.
            <br><br>
            As Hello Zenno is in its early stages, this policy is likely to evolve as the service develops.
            Your continued use after changes indicates acceptance of the updated policy.
          `
        }
      ]
    }
  ];
  
  // Flatten categories for the ToC and page rendering
  const allFaqs = privacyCategories.flatMap(category => category.faqs);
</script>

<svelte:head>
  <title>Privacy Policy | {SITE_NAME}</title>
  <meta name="description" content="Privacy Policy for Hello Zenno, explaining how we collect, use, and protect your information." />
</svelte:head>

<NebulaBackground>
  <!-- Privacy Policy Hero Section -->
  <section class="hero-section">
    <div class="container-fluid px-0">
      <div class="privacy-header">
        <div class="container py-4">
          <div class="row justify-content-center">
            <div class="col-12 text-center">
              <h1 class="display-4 fw-bold mb-3 hero-title">
                Privacy <span class="text-primary-green">Policy</span>
              </h1>
              <p class="subtitle mb-2">
                Last updated: {new Date().toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'})}
              </p>
              <p class="lead mb-3">
                <span class="badge bg-warning text-dark">Early Stage</span> This policy may evolve as Hello Zenno develops.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Privacy Content -->
  <section class="py-4">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          
          <!-- Table of Contents -->
          <TableOfContents categories={privacyCategories as any} />
          
          <!-- Privacy list - all visible and categorized -->
          <div class="privacy-list">
            {#each privacyCategories as category}
              <div id={category.id} class="category-container mb-4">
                <h2 class="h3 category-title mb-3 text-primary-green">{category.title}</h2>
                
                {#each category.faqs as faq}
                  <div class="privacy-item" id={faq.id}>
                    <div class="privacy-header">
                      <h3 class="h4 privacy-question mb-1 text-primary-green">
                        <a href="#{faq.id}" class="anchor-link">#</a>
                        {faq.question}
                      </h3>
                      <button 
                        class="btn-back-to-top" 
                        on:click={scrollToTop} 
                        aria-label="Back to top"
                      >
                        <ArrowUp size={20} weight="fill" />
                      </button>
                    </div>
                    <div class="privacy-answer">
                      {@html faq.answer}
                    </div>
                  </div>
                {/each}
              </div>
            {/each}
          </div>
          
          <!-- Contact section -->
          <div class="card contact-card p-4 text-center mt-4">
            <h3 class="mb-3">Questions about our Privacy Policy?</h3>
            <p class="mb-4">
              If you have questions or concerns about our data practices, please contact us directly.
            </p>
            <div class="d-flex justify-content-center gap-5 flex-wrap">
              <ContactButton 
                asButton={false}
                subject="Question about Hello Zenno Privacy Policy" 
                caption="Contact Us"
              ></ContactButton>
              
              <GithubIssueButton 
                asButton={false}
                caption="GitHub Issues"
              ></GithubIssueButton>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </section>
</NebulaBackground>

<style>
  /* Hero section styling - modified to start at the top */
  .hero-section {
    position: relative;
    padding-top: 0;
    z-index: 1;
    margin-top: 0;
  }
  
  .privacy-header {
    padding: 0px 0 20px;
  }
  
  .hero-title {
    position: relative;
    z-index: 2;
    color: #f8f9fa;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }
  
  .subtitle {
    position: relative;
    z-index: 2;
    color: #d7dadd;
  }
  
  .text-primary-green {
    color: var(--hz-color-primary-green);
  }
  
  /* Category styling */
  .category-container {
    padding-top: 1.5rem;
    border-top: 2px solid var(--hz-color-border);
  }
  
  .category-title {
    margin-bottom: 1.5rem;
    position: relative;
    display: inline-block;
  }
  
  .category-title::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 50px;
    height: 3px;
    background-color: var(--hz-color-primary-green);
    border-radius: 3px;
  }
  
  /* Privacy styling */
  .privacy-item {
    padding: 1.5rem;
    background-color: var(--hz-color-surface);
    border-radius: 8px;
    position: relative;
    border: 1px solid var(--hz-color-border);
    margin-bottom: 1.25rem;
    transition: all 0.2s ease;
  }
  
  .privacy-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: var(--hz-color-primary-green-dark);
  }
  
  .privacy-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.15rem;
  }
  
  .privacy-question {
    font-weight: 600;
    position: relative;
    margin: 0;
    padding-right: 2rem;
    font-size: 1.25rem;
  }
  
  .anchor-link {
    color: var(--hz-color-border);
    position: absolute;
    left: -1.5rem;
    text-decoration: none;
    font-weight: normal;
    opacity: 0.5;
    transition: opacity 0.2s ease;
  }
  
  .anchor-link:hover {
    opacity: 1;
    color: var(--hz-color-primary-green);
  }
  
  .btn-back-to-top {
    background-color: rgba(102, 154, 115, 0.05);
    border: 1px solid var(--hz-color-border);
    color: var(--hz-color-text-secondary);
    padding: 0.35rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.9;
    transition: all 0.2s ease;
    margin-top: -0.35rem;
  }
  
  .btn-back-to-top:hover {
    opacity: 1;
    color: var(--hz-color-primary-green);
    background-color: rgba(102, 154, 115, 0.15);
    border-color: var(--hz-color-primary-green);
    transform: translateY(-2px);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
  
  .privacy-answer {
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }
  
  /* Contact card */
  .contact-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  }
  
  /* Add responsive adjustments */
  @media (max-width: 768px) {
    .privacy-header {
      padding: 30px 0;
    }
    
    .anchor-link {
      opacity: 0.8;
      position: relative;
      left: 0;
      margin-right: 0.5rem;
    }
  }
</style> 