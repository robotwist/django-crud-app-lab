"""
End-to-End tests for Monolith: Artifact Archive

These tests verify the complete user journey through the application,
testing interactions between multiple components.
"""

import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from artifacts.models import Artifact, Category, Tag

User = get_user_model()

# Helper function to create a test image
def get_test_image_file(filename='test_image.jpg', content_type='image/jpeg'):
    file_path = os.path.join(os.path.dirname(__file__), 'test_files', filename)
    
    # Create test directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create a simple test image if it doesn't exist
    if not os.path.exists(file_path):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(file_path)
    
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(filename, f.read(), content_type=content_type)

class ArtifactArchiveE2ETest(StaticLiveServerTestCase):
    """End-to-end tests for the Monolith: Artifact Archive application."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configure Chrome options for headless operation
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the WebDriver
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)  # seconds
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Create test users and test data before each test."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test categories
        self.category = Category.objects.create(
            name='Vinyl Records',
            description='Analog audio recordings on vinyl discs'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='vintage')
        self.tag2 = Tag.objects.create(name='rare')
        
        # Create test artifact
        self.artifact = Artifact.objects.create(
            title='Test Vinyl Record',
            description='A test vinyl record for e2e testing',
            user=self.admin_user,
            category=self.category,
            popularity_score=50
        )
        self.artifact.tags.add(self.tag1, self.tag2)
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present on the page."""
        try:
            element = WebDriverWait(self.selenium, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Timed out waiting for element: {value}")
    
    def test_user_signup_and_login(self):
        """Test the user signup and login process."""
        # Navigate to the signup page
        self.selenium.get(f'{self.live_server_url}{reverse("users:signup")}')
        
        # Fill in the signup form
        self.selenium.find_element(By.NAME, 'username').send_keys('newuser')
        self.selenium.find_element(By.NAME, 'email').send_keys('new@example.com')
        self.selenium.find_element(By.NAME, 'password1').send_keys('complex-password-123')
        self.selenium.find_element(By.NAME, 'password2').send_keys('complex-password-123')
        
        # Submit the form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify we're redirected to login or dashboard
        self.wait_for_element(By.CSS_SELECTOR, '.messages')
        
        # Now logout and test login
        self.selenium.get(f'{self.live_server_url}{reverse("logout")}')
        
        # Go to login page
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        
        # Fill in the login form
        self.selenium.find_element(By.NAME, 'username').send_keys('newuser')
        self.selenium.find_element(By.NAME, 'password').send_keys('complex-password-123')
        
        # Submit the form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify we're logged in
        self.wait_for_element(By.CSS_SELECTOR, 'a[href*="user_profile"]')
        
        # Check that our username appears somewhere on the page
        self.assertTrue('newuser' in self.selenium.page_source)
    
    def test_create_artifact(self):
        """Test creating a new artifact."""
        # Login as a regular user
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        self.selenium.find_element(By.NAME, 'username').send_keys('testuser')
        self.selenium.find_element(By.NAME, 'password').send_keys('testpassword')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to the artifact creation page
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_create")}')
        
        # Fill in the artifact form
        self.selenium.find_element(By.NAME, 'title').send_keys('A New Test Artifact')
        self.selenium.find_element(By.NAME, 'description').send_keys('This is a detailed description of the test artifact.')
        
        # Select category from dropdown
        category_select = self.selenium.find_element(By.NAME, 'category')
        category_select.find_element(By.CSS_SELECTOR, f'option[value="{self.category.id}"]').click()
        
        # Add tags
        self.selenium.find_element(By.NAME, 'tags').send_keys('vintage, test, e2e')
        
        # Upload an image (this is complex in Selenium with file inputs, mocking for now)
        # In a real test, you would provide a path to a local test image
        
        # Submit the form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for the redirect to the artifact detail or list page
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-title, .artifact-list')
        
        # Verify the artifact was created
        self.assertTrue('A New Test Artifact' in self.selenium.page_source)
    
    def test_view_artifact_details(self):
        """Test viewing an artifact's details."""
        # Navigate to the artifact list page
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_list")}')
        
        # Find and click on our test artifact
        self.selenium.find_element(By.LINK_TEXT, 'Test Vinyl Record').click()
        
        # Verify we're on the artifact detail page
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-detail')
        
        # Check that the artifact details are displayed
        self.assertTrue('Test Vinyl Record' in self.selenium.page_source)
        self.assertTrue('A test vinyl record for e2e testing' in self.selenium.page_source)
        self.assertTrue('vintage' in self.selenium.page_source)
        self.assertTrue('rare' in self.selenium.page_source)
    
    def test_edit_artifact(self):
        """Test editing an existing artifact."""
        # Login as admin
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        self.selenium.find_element(By.NAME, 'username').send_keys('admin')
        self.selenium.find_element(By.NAME, 'password').send_keys('adminpassword')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to the artifact's edit page
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_update", args=[self.artifact.id])}')
        
        # Update the artifact title
        title_input = self.selenium.find_element(By.NAME, 'title')
        title_input.clear()
        title_input.send_keys('Updated Vinyl Record')
        
        # Update the description
        desc_input = self.selenium.find_element(By.NAME, 'description')
        desc_input.clear()
        desc_input.send_keys('This description has been updated')
        
        # Submit the form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for redirect to detail page
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-detail')
        
        # Verify the artifact was updated
        self.assertTrue('Updated Vinyl Record' in self.selenium.page_source)
        self.assertTrue('This description has been updated' in self.selenium.page_source)
    
    def test_delete_artifact(self):
        """Test deleting an artifact."""
        # Login as admin
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        self.selenium.find_element(By.NAME, 'username').send_keys('admin')
        self.selenium.find_element(By.NAME, 'password').send_keys('adminpassword')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to the artifact's delete page
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_delete", args=[self.artifact.id])}')
        
        # Confirm deletion
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for redirect to list page
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-list')
        
        # Verify the artifact was deleted
        self.assertFalse('Test Vinyl Record' in self.selenium.page_source)
    
    def test_full_user_journey(self):
        """
        Test a complete user journey from signup to creating, viewing,
        editing, and deleting an artifact.
        """
        # 1. User signs up
        self.selenium.get(f'{self.live_server_url}{reverse("users:signup")}')
        
        username = 'journey_user'
        self.selenium.find_element(By.NAME, 'username').send_keys(username)
        self.selenium.find_element(By.NAME, 'email').send_keys('journey@example.com')
        self.selenium.find_element(By.NAME, 'password1').send_keys('journey-password-123')
        self.selenium.find_element(By.NAME, 'password2').send_keys('journey-password-123')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 2. User logs in
        self.selenium.get(f'{self.live_server_url}{reverse("login")}')
        self.selenium.find_element(By.NAME, 'username').send_keys(username)
        self.selenium.find_element(By.NAME, 'password').send_keys('journey-password-123')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 3. User creates a new artifact
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_create")}')
        
        artifact_title = 'Journey Test Artifact'
        self.selenium.find_element(By.NAME, 'title').send_keys(artifact_title)
        self.selenium.find_element(By.NAME, 'description').send_keys('Created during the user journey test')
        
        category_select = self.selenium.find_element(By.NAME, 'category')
        category_select.find_element(By.CSS_SELECTOR, f'option[value="{self.category.id}"]').click()
        
        self.selenium.find_element(By.NAME, 'tags').send_keys('journey, test, e2e')
        
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 4. Find the artifact in the list
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_list")}')
        
        # Verify the artifact appears in the list
        self.assertTrue(artifact_title in self.selenium.page_source)
        
        # 5. View the artifact details - find it by title
        self.selenium.find_element(By.LINK_TEXT, artifact_title).click()
        
        # Verify we're on the details page
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-detail')
        self.assertTrue('Created during the user journey test' in self.selenium.page_source)
        
        # 6. Edit the artifact - assuming there's an edit link on the detail page
        try:
            self.selenium.find_element(By.LINK_TEXT, 'Edit').click()
        except NoSuchElementException:
            # If there's no direct link, navigate by URL
            # We need to get the ID of the artifact we just created
            # For simplicity in this test, we'll just go back to the list and select again
            self.selenium.get(f'{self.live_server_url}{reverse("artifact_list")}')
            artifact_id = Artifact.objects.get(title=artifact_title).id
            self.selenium.get(f'{self.live_server_url}{reverse("artifact_update", args=[artifact_id])}')
        
        # Update fields
        updated_title = 'Updated Journey Artifact'
        title_input = self.selenium.find_element(By.NAME, 'title')
        title_input.clear()
        title_input.send_keys(updated_title)
        
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 7. Verify the update
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-detail')
        self.assertTrue(updated_title in self.selenium.page_source)
        
        # 8. Delete the artifact
        try:
            self.selenium.find_element(By.LINK_TEXT, 'Delete').click()
        except NoSuchElementException:
            # If there's no direct link, navigate by URL
            artifact_id = Artifact.objects.get(title=updated_title).id
            self.selenium.get(f'{self.live_server_url}{reverse("artifact_delete", args=[artifact_id])}')
        
        # Confirm deletion
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Verify deletion
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-list')
        self.assertFalse(updated_title in self.selenium.page_source)
        
        # 9. User logs out
        self.selenium.find_element(By.LINK_TEXT, 'Logout').click()
        
        # Verify logout was successful
        self.assertTrue('Login' in self.selenium.page_source)

    def test_search_functionality(self):
        """Test the artifact search functionality."""
        # Create some artifacts with distinct titles
        Artifact.objects.create(
            title='Rare Beatles Vinyl',
            description='Original pressing of Abbey Road',
            user=self.admin_user,
            category=self.category,
            popularity_score=80
        )
        
        Artifact.objects.create(
            title='Vintage Typewriter',
            description='Excellent condition Smith Corona',
            user=self.admin_user,
            category=self.category,
            popularity_score=65
        )
        
        # Navigate to the search page or list page with search
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_list")}')
        
        # Search for "Beatles"
        search_input = self.selenium.find_element(By.NAME, 'q')
        search_input.send_keys('Beatles')
        search_input.submit()
        
        # Verify search results
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-list')
        self.assertTrue('Rare Beatles Vinyl' in self.selenium.page_source)
        self.assertFalse('Vintage Typewriter' in self.selenium.page_source)
        
        # Clear search and try another term
        self.selenium.get(f'{self.live_server_url}{reverse("artifact_list")}')
        search_input = self.selenium.find_element(By.NAME, 'q')
        search_input.send_keys('Vintage')
        search_input.submit()
        
        # Verify the new search results
        self.wait_for_element(By.CSS_SELECTOR, '.artifact-list')
        self.assertTrue('Vintage Typewriter' in self.selenium.page_source)
        self.assertFalse('Rare Beatles Vinyl' in self.selenium.page_source)

# Add more tests as needed for your specific application features 