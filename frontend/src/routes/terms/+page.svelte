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
  
  // Terms of Service data grouped by categories
  const tosCategories = [
    {
      id: "introduction",
      title: "Introduction",
      faqs: [
        {
          id: "welcome",
          question: "Welcome to Hello Zenno",
          answer: `
            Hello Zenno is an open-source web application for intermediate and advanced language learners. 
            These Terms of Service govern your use of our website, tools, and services.
            <br><br>
            <strong>Please note:</strong> Hello Zenno is currently in its earliest stages of development. 
            These terms are subject to change as the site evolves. We'll make reasonable efforts to notify users 
            of significant changes.
          `
        },
        {
          id: "agreement",
          question: "Agreement to Terms",
          answer: `
            By accessing or using Hello Zenno, you agree to be bound by these Terms of Service. 
            If you disagree with any part of these terms, you may not access or use our services.
          `
        }
      ]
    },
    {
      id: "account",
      title: "Account & Access",
      faqs: [
        {
          id: "eligibility",
          question: "Eligibility",
          answer: `
            You must be at least 13 years old to use Hello Zenno. If you are under 18, you should have 
            your parent or guardian's permission to use our services. By using Hello Zenno, you represent 
            that you meet these requirements.
          `
        },
        {
          id: "account-creation",
          question: "Account Creation",
          answer: `
            When you create an account, you must provide accurate information. You're responsible for 
            maintaining the security of your account and password. Hello Zenno cannot and will not be 
            liable for any loss or damage from your failure to comply with this security obligation.
          `
        },
        {
          id: "access-restrictions",
          question: "Access Restrictions",
          answer: `
            Much of the site is world-readable and free to access. Some features require login 
            (particularly AI-generated content). The login requirement is implemented to prevent 
            bot abuse that could trigger expensive AI generation costs.
            <br><br>
            We reserve the right to refuse service, terminate accounts, or restrict access to anyone for any reason.
          `
        }
      ]
    },
    {
      id: "content",
      title: "Content & Uploads",
      faqs: [
        {
          id: "user-uploads",
          question: "User-Uploaded Content",
          answer: `
            Hello Zenno allows users to upload various types of content including text, URLs, MP3 audio files, 
            and images. <strong>Please note that currently, all uploads are visible to other users</strong>. 
            There is no mechanism to mark content as private.
            <br><br>
            By uploading content, you represent that you have the rights to do so, and you grant Hello Zenno a 
            license to process, display, and store this content to provide our services.
          `
        },
        {
          id: "intellectual-property",
          question: "Intellectual Property Rights",
          answer: `
            All AI-generated content (dictionary entries, example sentences, translations, etc.) is owned by 
            Hello Zenno, even if generated at a user's request. This content remains available to all users.
            <br><br>
            You're responsible for ensuring you have the rights to upload and share any content you provide.
            Only upload content that is public domain or that you have permission to share.
          `
        },
        {
          id: "content-guidelines",
          question: "Content Guidelines",
          answer: `
            You agree not to upload content that:
            <ul>
              <li>Is illegal, harmful, threatening, abusive, harassing, or defamatory</li>
              <li>Infringes on intellectual property rights without permission</li>
              <li>Contains malware or attempts to compromise site security</li>
              <li>Is intentionally misleading or fraudulent</li>
              <li>Contains sexually explicit material or shares personal data of others without consent</li>
            </ul>
            Hello Zenno reserves the right to remove content that violates these guidelines.
          `
        }
      ]
    },
    {
      id: "services",
      title: "Services & Limitations",
      faqs: [
        {
          id: "service-description",
          question: "Service Description",
          answer: `
            Hello Zenno offers language learning tools including enhanced text reading, AI-generated dictionary entries,
            and audio generation for listening practice. The service is designed for intermediate and advanced learners
            and is not a complete language learning solution.
          `
        },
        {
          id: "third-party-integration",
          question: "Third-Party AI Integrations",
          answer: `
            Our services integrate with third-party AI services including:
            <ul>
              <li>Anthropic Claude for dictionary entries and text processing</li>
              <li>Eleven Labs for generating audio from text</li>
              <li>Potentially other AI providers for specific language tasks</li>
            </ul>
            Your content may be sent to these services for processing. All data shared with these services is solely 
            for providing Hello Zenno's core functionality.
          `
        },
        {
          id: "service-limitations",
          question: "Service Limitations & Disclaimers",
          answer: `
            <strong>Hello Zenno is provided "as is" without warranty of any kind.</strong> We do not guarantee:
            <ul>
              <li>The accuracy, completeness, or reliability of any AI-generated content</li>
              <li>Uninterrupted, secure, or error-free operation</li>
              <li>That our services will meet your specific requirements</li>
            </ul>
            As an educational tool, Hello Zenno is not a substitute for professional language instruction. Content is 
            intended for learning purposes only and should not be relied upon for professional, academic, or assessment contexts.
          `
        }
      ]
    },
    {
      id: "data",
      title: "Data & Privacy",
      faqs: [
        {
          id: "data-collection",
          question: "Data Collection",
          answer: `
            We collect information necessary to provide our services, including:
            <ul>
              <li>Account information (username, email)</li>
              <li>Content you upload</li>
              <li>Technical data (IP addresses, analytics)</li>
            </ul>
            Please see our <a href="/privacy">Privacy Policy</a> for more details about how we handle your data.
          `
        },
        {
          id: "data-retention",
          question: "Data Retention",
          answer: `
            We retain uploaded texts and AI-generated content indefinitely unless you request deletion.
            User-specific data (preferences, "ignored words" lists, etc.) is retained until you delete your account.
          `
        },
        {
          id: "account-deletion",
          question: "Account Deletion",
          answer: `
            You can request account deletion by contacting ${CONTACT_EMAIL}. Upon deletion, we will remove your:
            <ul>
              <li>Personal identifiable information (email address)</li>
              <li>User preferences</li>
              <li>User-specific data such as "ignored words" lists</li>
            </ul>
            AI-generated content, public source files, and anonymous usage data will be retained.
          `
        }
      ]
    },
    {
      id: "liability",
      title: "Liability & Legal",
      faqs: [
        {
          id: "limitation-liability",
          question: "Limitation of Liability",
          answer: `
            To the maximum extent permitted by applicable law, Hello Zenno and its affiliates, officers, employees, 
            agents, partners and licensors shall not be liable for any direct, indirect, incidental, special, 
            consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, 
            or other intangible losses, resulting from:
            <ul>
              <li>Your access to or use of or inability to access or use the service</li>
              <li>Any conduct or content of any third party on the service</li>
              <li>Any content obtained from the service</li>
              <li>Unauthorized access, use or alteration of your transmissions or content</li>
            </ul>
          `
        },
        {
          id: "indemnification",
          question: "Indemnification",
          answer: `
            You agree to defend, indemnify and hold harmless Hello Zenno and its licensors from and against any claims, 
            liabilities, damages, losses, and expenses arising out of or in any way connected with your use of our services 
            or your violation of these Terms.
          `
        },
        {
          id: "governing-law",
          question: "Governing Law",
          answer: `
            These Terms shall be governed by the laws of the jurisdiction in which Hello Zenno operates, without 
            regard to its conflict of law provisions.
          `
        }
      ]
    },
    {
      id: "changes",
      title: "Changes & Contact",
      faqs: [
        {
          id: "changes-to-terms",
          question: "Changes to Terms",
          answer: `
            We reserve the right to modify these terms at any time. We will provide notice of significant changes. 
            Your continued use of Hello Zenno after such modifications constitutes your acceptance of the updated terms.
            <br><br>
            As Hello Zenno is in its early stages, these terms are likely to evolve as the service develops.
          `
        }
      ]
    }
  ];
  
  // Flatten categories for the ToC and page rendering
  const allFaqs = tosCategories.flatMap(category => category.faqs);
</script>

<svelte:head>
  <title>Terms of Service | {SITE_NAME}</title>
  <meta name="description" content="Terms of Service for Hello Zenno, the AI-powered language learning assistant." />
</svelte:head>

<NebulaBackground>
  <!-- Terms of Service Hero Section -->
  <section class="hero-section">
    <div class="container-fluid px-0">
      <div class="terms-header">
        <div class="container py-4">
          <div class="row justify-content-center">
            <div class="col-12 text-center">
              <h1 class="display-4 fw-bold mb-3 hero-title">
                Terms of <span class="text-primary-green">Service</span>
              </h1>
              <p class="subtitle mb-2">
                Last updated: {new Date().toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'})}
              </p>
              <p class="lead mb-3">
                <span class="badge bg-warning text-dark">Early Stage</span> These terms may evolve as Hello Zenno develops.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Terms Content -->
  <section class="py-4">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          
          <!-- Table of Contents -->
          <TableOfContents categories={tosCategories as any} />
          
          <!-- Terms list - all visible and categorized -->
          <div class="terms-list">
            {#each tosCategories as category}
              <div id={category.id} class="category-container mb-4">
                <h2 class="h3 category-title mb-3 text-primary-green">{category.title}</h2>
                
                {#each category.faqs as faq}
                  <div class="terms-item" id={faq.id}>
                    <div class="terms-header">
                      <h3 class="h4 terms-question mb-1 text-primary-green">
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
                    <div class="terms-answer">
                      {@html faq.answer}
                    </div>
                  </div>
                {/each}
              </div>
            {/each}
          </div>
          
          <!-- Contact section -->
          <div class="card contact-card p-4 text-center mt-4">
            <h3 class="mb-3">Questions about our Terms?</h3>
            <p class="mb-4">
              If you have questions or concerns about these terms, please contact us directly.
            </p>
            <div class="d-flex justify-content-center gap-5 flex-wrap">
              <ContactButton 
                asButton={false}
                subject="Question about Hello Zenno Terms of Service" 
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
  
  .terms-header {
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
  
  /* Terms styling */
  .terms-item {
    padding: 1.5rem;
    background-color: var(--hz-color-surface);
    border-radius: 8px;
    position: relative;
    border: 1px solid var(--hz-color-border);
    margin-bottom: 1.25rem;
    transition: all 0.2s ease;
  }
  
  .terms-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: var(--hz-color-primary-green-dark);
  }
  
  .terms-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.15rem;
  }
  
  .terms-question {
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
  
  .terms-answer {
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
    .terms-header {
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