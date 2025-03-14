from playwright.sync_api import Page, expect
import time

def test_minilemma_component(page: Page):
    """Test that the MiniLemma component renders correctly."""
    # Navigate to the test page with a longer timeout
    page.set_default_timeout(60000)  # 60 seconds
    
    # Log console messages for debugging
    logs = []
    
    def log_console_message(msg):
        text = f"{msg.type}: {msg.text}"
        if msg.type == "error" and "Failed to load resource" in msg.text:
            # Extract the URL from the error message if possible
            url_info = str(msg.location)
            text += f" (URL: {url_info})"
        
        print(f"BROWSER LOG: {text}")
        logs.append(text)
    
    page.on("console", log_console_message)
    
    try:
        # Navigate to the test page
        response = page.goto("/minilemma-test")
        assert response is not None, "No response received from page"
        assert response.ok, f"Page load failed with status {response.status}"
        
        # Verify page title
        expect(page).to_have_title("MiniLemma Test - Hello Zenno")
        
        # Wait a bit to ensure the page has fully loaded
        time.sleep(2)
        
        # Take a screenshot for visual inspection
        page.screenshot(path="minilemma_test.png")
        
        # Check for component mount point - use first() to handle multiple elements
        mount_point = page.locator("#mini-lemma-test").first
        expect(mount_point).to_be_visible()
        
        # Check for component data display
        pre_element = page.locator("pre")
        expect(pre_element).to_contain_text("γράφω")
        
        # Check fallback rendering
        fallback_lemma = page.locator(".mini-lemma .lemma-text")
        expect(fallback_lemma).to_have_text("γράφω")
        
        # Output the page content for debugging
        print(f"Page title: {page.title()}")
        print(f"Page URL: {page.url}")
        
        # Get the HTML source and check what's happening with the mount point
        html_source = page.content()
        print("\nMount point HTML:")
        mount_point_html = page.locator("#mini-lemma-test").count()
        print(f"Number of elements with ID mini-lemma-test: {mount_point_html}")
        
        # Examine the script tags in the page
        script_tags = page.locator("script")
        script_count = script_tags.count()
        print(f"\nFound {script_count} script tags:")
        for i in range(script_count):
            script = script_tags.nth(i)
            script_src = script.get_attribute("src") or script.get_attribute("type") or "inline script"
            print(f"  Script {i+1}: {script_src}")
        
        # Print all logs
        print("\nConsole logs collected:")
        for log in logs:
            print(f"- {log}")
        
    except Exception as e:
        # Take a screenshot on failure
        page.screenshot(path="minilemma_test_error.png")
        print(f"Error during test: {str(e)}")
        print(f"Current URL: {page.url}")
        raise