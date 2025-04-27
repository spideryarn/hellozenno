# Hello Zenno - Terms and Privacy FAQ

This document contains the information needed to draft formal Terms of Service and Privacy Policy documents for Hello Zenno.

see:
- /terms
- /privacy

see also:
- README.md
- marketing/MARKETING_EXPLAINER_NOTES.md
- About, FAQ

## Availability and Access

- **Global Availability**: Hello Zenno is available worldwide as a web application.
- **Free vs. Login-Required Content**: 
  - Much of the site is world-readable and free to access
  - Some features require login (particularly AI-generated content)
  - Login requirement implemented to prevent bot abuse triggering expensive AI generation
  - May potentially charge for some AI generation features in the future

## User Age Requirements

- **Target Audience**: Currently intended to be available to everyone, with no specific age restrictions
- **Content Considerations**: 
  - User-uploaded content may potentially include adult themes (articles about sex, stories with violence, etc.)
  - Need to evaluate legal requirements for children's access (COPPA, etc.)

## Data Collection

- **Account Creation Data**:
  - Username
  - Email address
  - Password
  - Google sign-in (planned support)
- **Technical Data**:
  - IP addresses
  - Analytics data via Google Analytics

## Cookies and Tracking

- **Cookie Usage**: Yes
  - Authentication (login status)
  - Analytics (Google Analytics)
  - Other standard website functionality

## Data Retention

- **Current Policy**: No defined deletion/retention policy (new website)
- **Preferences**:
  - Would like to retain uploaded texts indefinitely
  - Would like to retain AI-generated content indefinitely
  - Need to evaluate legal requirements for data retention policies

## Data Sharing

- **Third-Party Data Selling**: No user data is sold to third parties
- **Data Sharing**:
  - Data processors (Google Analytics and potentially advertising in future)
  - AI model companies (for processing and providing site functionality only)
  - No sharing with external partners for marketing purposes

## Third-Party AI Integrations

- **Large Language Models (LLMs)**:
  - Anthropic Claude for dictionary entries and text processing
  - Potentially OpenAI and Google Gemini for certain language tasks
  - User inputs may be sent to these services for processing
- **Text-to-Speech**:
  - Eleven Labs for generating audio from text
  - Text content is sent to generate spoken versions
- **Purpose of Data Sharing**:
  - All data shared with these services is solely for providing core functionality
  - Data is processed and not retained beyond service requirements
  - No marketing or secondary usage of this data

## User-Uploaded Content

- **Types of Content Users Can Upload**:
  - Text (directly pasted/typed)
  - URLs (to download content from)
  - MP3 audio files
  - Images (e.g., photographs of books or magazine text)
- **Content Moderation**:
  - Currently no filters or special checks on uploaded content
  - No specific rules regarding offensive, copyrighted, or problematic content
- **Content Visibility**:
  - Currently no mechanism for users to mark content as public or private
  - All uploaded content is potentially viewable by other users

## User Data Rights & Account Deletion

- **Account Deletion Process**:
  - No automated account deletion functionality currently available
  - Users can request account deletion by contacting hello@hellozenno.com
  - Requests will be processed promptly
- **Data Deleted Upon Account Removal**:
  - Personal Identifiable Information (PII) such as email address
  - User preferences (e.g., target language selection)
  - User-specific data such as "ignored words" list
  - (Future feature) Private source files if/when implemented
- **Data Retained After Account Deletion**:
  - AI-generated content such as dictionary entries and sentences
  - Public source files and their derivatives
  - Anonymous usage data previously sent to analytics services
  - Content contributed to the global knowledge base
- **Data Ownership**:
  - All AI-generated content is considered property of Hello Zenno, even if generated at a user's request
  - This content remains available to all users after the requesting user's account deletion

## Intellectual Property Rights

- **AI-Generated Content**:
  - All dictionary entries, example sentences, translations, and other AI-generated content are owned by Hello Zenno
  - This applies regardless of user login status or whether the user paid for services
  - Even when users provide their own API keys for generation (future feature), Hello Zenno claims ownership of the resulting content
  - Hello Zenno reserves the right to make this content freely available to other users and potentially via public API
  - AI-generated content may be licensed for use by others at Hello Zenno's discretion
- **User-Uploaded Content**:
  - Rights and ownership of user-uploaded content need further clarification
  - Users are responsible for ensuring they have the rights to upload and share content
  - Hello Zenno needs a license to process, display, and store user-uploaded content to provide services

## Prohibited Behaviors and User Conduct

- **Forbidden Activities**:
  - Illegal activities of any kind
  - Creating or distributing harmful or malicious content
  - Harassment, threats, or intimidation of others
  - Impersonation of other individuals or entities
  - Uploading content that infringes on intellectual property rights
  - Attempting to compromise site security or functionality
  - Creating misleading or fraudulent content
  - Intentionally uploading sexually explicit or obscene material
  - Sharing personal data of others without consent
  - Abusing the service's AI generation capabilities
- **Content Guidelines**:
  - Users should avoid uploading offensive content when possible
  - Clear citation of sources is encouraged for uploaded text
  - Respect intellectual property rights of original content creators
  - Consider the educational purpose of the platform when uploading materials
- **Enforcement**:
  - Hello Zenno reserves the right to remove content that violates terms
  - Account suspension or termination may result from repeated violations
  - Users can report problematic content to hello@hellozenno.com
  - No obligation to proactively monitor all user content

## User Feedback and Support

- **Reporting Issues**:
  - Users can report technical issues, bugs, or concerns via email at hello@hellozenno.com
  - For open-source related issues or feature requests, users can create a GitHub issue at https://github.com/spideryarn/hellozenno/issues
- **Content Reporting**:
  - Problematic or inappropriate content can be reported via email
  - Copyright infringement or DMCA-related concerns should be sent to hello@hellozenno.com
- **Feature Requests**:
  - Users can suggest new features or improvements through GitHub issues
  - Email feedback is also accepted at hello@hellozenno.com
- **Response Time**:
  - No guaranteed response time as this is an open-source project
  - More critical issues (security, inappropriate content) will be prioritized

## Security Measures

- **Authentication Security**:
  - Implemented using Supabase authentication
  - Passwords are securely hashed using bcrypt (industry standard)
  - JWT (JSON Web Tokens) for session management
  - Authentication state can be validated on both client and server
- **Data Security**:
  - All data transmitted via HTTPS encryption (through Vercel deployment)
  - Database secured with Supabase's security practices
  - Data encrypted at rest with AES-256 through Supabase
- **Third-party Security**:
  - Supabase is SOC 2 Type 2 compliant for handling sensitive data
  - Vercel provides additional security through serverless deployment
- **Backend API Protection**:
  - JWT verification for protected API endpoints
  - Optional authentication for some endpoints (allowing anonymous access for read-only)
  - Server-side validation of user permissions

## Needs Further Discussion

- Legal requirements for minimum age restrictions
- Whether a specific data retention/deletion policy is legally required
- How to handle potentially adult content that users might upload
- Whether to implement content moderation policies for offensive or problematic content
- Copyright implications of user-uploaded content
- Implementation of public/private visibility controls for user content
- Clarification of intellectual property rights for user-uploaded content
- Potential licensing terms for AI-generated content if made available via API
- User liability for breaking terms or uploading illegal content:
  - How to handle uploads of copyrighted material
  - Policies for content that violates laws in certain jurisdictions
  - Process for handling DMCA takedown requests
  - User responsibility vs. platform responsibility
  - Terms for account termination in case of violations
- Limitations of liability and disclaimer of warranties:
  - Extent of responsibility for AI-generated content accuracy
  - Liability for service interruptions or data loss
  - Disclaimers regarding educational content and specialized advice
  - Warranty disclaimers for "as is" service provision
  - Caps on damages in case of legal disputes

## Additional Notes from 2024-06-09 Discussion

### Clarified Positions

#### Data Retention
- **Public Content**: All public uploaded texts and AI-generated content will be retained indefinitely
- **User-Specific Data**: Will be retained until the user deletes their account or requests for it to be deleted

#### Limitations of Liability
- **AI Content Accuracy**: Full disclaimer of responsibility for AI-generated content:
  > "All AI-generated content is provided 'as is' without warranty of any kind. We do not guarantee the accuracy, completeness, or reliability of any AI-generated content. No human review is performed, and users rely on such content at their own risk."

- **Service Interruptions**: Standard disclaimer needed:
  > "We do not guarantee uninterrupted, secure, or error-free operation of our services. We expressly disclaim liability for any service downtime, data loss, or performance issues."

- **Damages**: Comprehensive liability limitation approach:
  > "TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, HELLO ZENNO AND ITS AFFILIATES, OFFICERS, EMPLOYEES, AGENTS, PARTNERS AND LICENSORS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES, RESULTING FROM: (i) YOUR ACCESS TO OR USE OF OR INABILITY TO ACCESS OR USE THE SERVICE; (ii) ANY CONDUCT OR CONTENT OF ANY THIRD PARTY ON THE SERVICE; (iii) ANY CONTENT OBTAINED FROM THE SERVICE; AND (iv) UNAUTHORIZED ACCESS, USE OR ALTERATION OF YOUR TRANSMISSIONS OR CONTENT, WHETHER BASED ON WARRANTY, CONTRACT, TORT (INCLUDING NEGLIGENCE) OR ANY OTHER LEGAL THEORY, WHETHER OR NOT WE HAVE BEEN INFORMED OF THE POSSIBILITY OF SUCH DAMAGE."

  With optional fallback if needed in some jurisdictions:
  > "IF THE FOREGOING DISCLAIMER IS FOUND TO BE INVALID IN SOME JURISDICTIONS, OUR TOTAL LIABILITY TO YOU SHALL NOT EXCEED THE GREATER OF (a) THE AMOUNT PAID BY YOU TO US IN THE SIX (6) MONTHS PRECEDING THE EVENT GIVING RISE TO THE CLAIM, OR (b) $50 USD."

- **Educational Content**: Educational purpose disclaimer needed:
  > "Hello Zenno is an educational tool, not a substitute for professional language instruction. Content is intended for learning purposes only and should not be relied upon for professional, academic, or assessment contexts. We make no representations about the suitability of our content for any purpose."

### Outstanding Issues to Resolve
- Age restrictions and COPPA compliance
- User content visibility controls and handling of sensitive content
- Intellectual property rights for user-uploaded content
- Process for handling potentially copyrighted material and DMCA takedowns

## Additional Notes from 2024-06-10 Discussion

### Age Restrictions
- **Minimum Age**: Users must be 13 years or older to use the service
- This approach helps avoid COPPA compliance requirements
- Terms should state that:
  - Users must be 13+ to use the service
  - Users under 18 should have parental consent
  - Hello Zenno reserves the right to terminate accounts if users are discovered to be under 13

### Temporary Solution for User Uploads and Copyright
Until more comprehensive policies can be developed, the following temporary approach will be implemented:

1. **Public Nature of Uploads**: Clear disclaimers that all uploads are public and visible to all users
2. **User Responsibility**: Explicit statements that users must only upload content they have rights to
3. **Basic DMCA Process**: Provision of a copyright contact email (hello@hellozenno.com) for takedown requests
4. **Evolving Policies**: Notice that these policies are preliminary and subject to change as the service develops

This temporary solution will be refined over time to provide more comprehensive protection and clearer user expectations.
