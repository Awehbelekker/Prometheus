"""
Social Media Authentication Module for MASS Framework

This module implements OAuth2-based social media authentication for popular platforms
including Google, Facebook, GitHub, Microsoft, LinkedIn, and Twitter/X.

Features:
- Multi-provider OAuth2 support
- Secure token management
- User profile synchronization
- Account linking capabilities
- Provider-specific scopes and permissions
"""

import os
import secrets
import hashlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import aiohttp
import jwt
from cryptography.fernet import Fernet
import json
import base64
from urllib.parse import urlencode, parse_qs
import logging

logger = logging.getLogger(__name__)


@dataclass
class SocialProvider:
    """Configuration for a social media authentication provider"""
    name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scopes: List[str] = field(default_factory=list)
    redirect_uri: str = ""
    icon: str = ""
    color: str = ""


@dataclass
class SocialUser:
    """User information from social media provider"""
    provider: str
    provider_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    username: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAuthManager:
    """Manages social media authentication for multiple providers"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.providers: Dict[str, SocialProvider] = {}
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self._setup_default_providers()
    
    def _setup_default_providers(self):
        """Setup default social media providers"""
        
        # Google OAuth2
        self.providers["google"] = SocialProvider(
            name="Google",
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            auth_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            scopes=["openid", "email", "profile"],
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"),
            icon="fab fa-google",
            color="#4285f4"
        )
        
        # Facebook OAuth2
        self.providers["facebook"] = SocialProvider(
            name="Facebook",
            client_id=os.getenv("FACEBOOK_CLIENT_ID", ""),
            client_secret=os.getenv("FACEBOOK_CLIENT_SECRET", ""),
            auth_url="https://www.facebook.com/v18.0/dialog/oauth",
            token_url="https://graph.facebook.com/v18.0/oauth/access_token",
            user_info_url="https://graph.facebook.com/v18.0/me",
            scopes=["email", "public_profile"],
            redirect_uri=os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback"),
            icon="fab fa-facebook-f",
            color="#1877f2"
        )
        
        # GitHub OAuth2
        self.providers["github"] = SocialProvider(
            name="GitHub",
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user",
            scopes=["user:email"],
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"),
            icon="fab fa-github",
            color="#333333"
        )
        
        # Microsoft OAuth2
        self.providers["microsoft"] = SocialProvider(
            name="Microsoft",
            client_id=os.getenv("MICROSOFT_CLIENT_ID", ""),
            client_secret=os.getenv("MICROSOFT_CLIENT_SECRET", ""),
            auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            user_info_url="https://graph.microsoft.com/v1.0/me",
            scopes=["openid", "email", "profile"],
            redirect_uri=os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback"),
            icon="fab fa-microsoft",
            color="#00a1f1"
        )
        
        # LinkedIn OAuth2
        self.providers["linkedin"] = SocialProvider(
            name="LinkedIn",
            client_id=os.getenv("LINKEDIN_CLIENT_ID", ""),
            client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", ""),
            auth_url="https://www.linkedin.com/oauth/v2/authorization",
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            user_info_url="https://api.linkedin.com/v2/people/~",
            scopes=["r_liteprofile", "r_emailaddress"],
            redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/auth/linkedin/callback"),
            icon="fab fa-linkedin-in",
            color="#0077b5"
        )
        
        # Twitter/X OAuth2
        self.providers["twitter"] = SocialProvider(
            name="Twitter",
            client_id=os.getenv("TWITTER_CLIENT_ID", ""),
            client_secret=os.getenv("TWITTER_CLIENT_SECRET", ""),
            auth_url="https://twitter.com/i/oauth2/authorize",
            token_url="https://api.twitter.com/2/oauth2/token",
            user_info_url="https://api.twitter.com/2/users/me",
            scopes=["tweet.read", "users.read"],
            redirect_uri=os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/auth/twitter/callback"),
            icon="fab fa-twitter",
            color="#1da1f2"
        )
    
    def get_auth_url(self, provider_name: str, state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL for a provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        provider = self.providers[provider_name]
        
        if not provider.client_id:
            raise ValueError(f"Client ID not configured for {provider_name}")
        
        state = state or secrets.token_urlsafe(32)
        
        params = {
            "client_id": provider.client_id,
            "response_type": "code",
            "redirect_uri": provider.redirect_uri,
            "scope": " ".join(provider.scopes),
            "state": state,
        }
        
        # Provider-specific parameters
        if provider_name == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider_name == "microsoft":
            params["response_mode"] = "query"
        elif provider_name == "twitter":
            params["code_challenge"] = self._generate_pkce_challenge()
            params["code_challenge_method"] = "S256"
        
        return f"{provider.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, provider_name: str, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        provider = self.providers[provider_name]
        
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": provider.redirect_uri,
        }
        
        headers = {"Accept": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(provider.token_url, data=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Token exchange failed: {error_text}")
                
                return await response.json()
    
    async def get_user_info(self, provider_name: str, access_token: str) -> SocialUser:
        """Get user information from provider using access token"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        provider = self.providers[provider_name]
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            # Get basic user info
            user_url = provider.user_info_url
            if provider_name == "facebook":
                user_url += "?fields=id,name,email,picture"
            elif provider_name == "linkedin":
                user_url += ":(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
            
            async with session.get(user_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"User info request failed: {error_text}")
                
                user_data = await response.json()
            
            # Get email for providers that require separate call
            email = None
            if provider_name == "github":
                async with session.get("https://api.github.com/user/emails", headers=headers) as email_response:
                    if email_response.status == 200:
                        emails = await email_response.json()
                        primary_email = next((e for e in emails if e.get("primary")), emails[0] if emails else None)
                        email = primary_email.get("email") if primary_email else None
            elif provider_name == "linkedin":
                async with session.get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))", headers=headers) as email_response:
                    if email_response.status == 200:
                        email_data = await email_response.json()
                        elements = email_data.get("elements", [])
                        if elements:
                            email = elements[0].get("handle~", {}).get("emailAddress")
            
            return self._parse_user_data(provider_name, user_data, email, access_token)
    
    def _parse_user_data(self, provider_name: str, user_data: Dict[str, Any], email: Optional[str], access_token: str) -> SocialUser:
        """Parse user data from different providers into a unified format"""
        
        if provider_name == "google":
            return SocialUser(
                provider=provider_name,
                provider_id=user_data.get("id"),
                email=user_data.get("email"),
                name=user_data.get("name"),
                avatar_url=user_data.get("picture"),
                raw_data=user_data,
                access_token=access_token
            )
        
        elif provider_name == "facebook":
            return SocialUser(
                provider=provider_name,
                provider_id=user_data.get("id"),
                email=user_data.get("email"),
                name=user_data.get("name"),
                avatar_url=user_data.get("picture", {}).get("data", {}).get("url"),
                raw_data=user_data,
                access_token=access_token
            )
        
        elif provider_name == "github":
            return SocialUser(
                provider=provider_name,
                provider_id=str(user_data.get("id")),
                email=email or user_data.get("email"),
                name=user_data.get("name") or user_data.get("login"),
                username=user_data.get("login"),
                avatar_url=user_data.get("avatar_url"),
                raw_data=user_data,
                access_token=access_token
            )
        
        elif provider_name == "microsoft":
            return SocialUser(
                provider=provider_name,
                provider_id=user_data.get("id"),
                email=user_data.get("mail") or user_data.get("userPrincipalName"),
                name=user_data.get("displayName"),
                raw_data=user_data,
                access_token=access_token
            )
        
        elif provider_name == "linkedin":
            first_name = user_data.get("firstName", {}).get("localized", {}).get("en_US", "")
            last_name = user_data.get("lastName", {}).get("localized", {}).get("en_US", "")
            name = f"{first_name} {last_name}".strip()
            
            avatar_url = None
            picture = user_data.get("profilePicture", {}).get("displayImage~", {}).get("elements", [])
            if picture:
                avatar_url = picture[0].get("identifiers", [{}])[0].get("identifier")
            
            return SocialUser(
                provider=provider_name,
                provider_id=user_data.get("id"),
                email=email,
                name=name,
                avatar_url=avatar_url,
                raw_data=user_data,
                access_token=access_token
            )
        
        elif provider_name == "twitter":
            return SocialUser(
                provider=provider_name,
                provider_id=user_data.get("data", {}).get("id"),
                email=None,  # Twitter doesn't provide email by default
                name=user_data.get("data", {}).get("name"),
                username=user_data.get("data", {}).get("username"),
                avatar_url=user_data.get("data", {}).get("profile_image_url"),
                raw_data=user_data,
                access_token=access_token
            )
        
        else:
            # Generic parser for unknown providers
            return SocialUser(
                provider=provider_name,
                provider_id=str(user_data.get("id", user_data.get("sub"))),
                email=user_data.get("email"),
                name=user_data.get("name", user_data.get("display_name")),
                avatar_url=user_data.get("picture", user_data.get("avatar_url")),
                raw_data=user_data,
                access_token=access_token
            )
    
    def _generate_pkce_challenge(self) -> str:
        """Generate PKCE code challenge for OAuth2 PKCE flow"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_challenge
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt sensitive token data"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt sensitive token data"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def get_provider_config(self, provider_name: str) -> Optional[SocialProvider]:
        """Get configuration for a specific provider"""
        return self.providers.get(provider_name)
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all configured providers with their display information"""
        return [
            {
                "name": provider.name,
                "key": key,
                "icon": provider.icon,
                "color": provider.color,
                "configured": bool(provider.client_id)
            }
            for key, provider in self.providers.items()
        ]
    
    async def refresh_access_token(self, provider_name: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        provider = self.providers[provider_name]
        
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        headers = {"Accept": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(provider.token_url, data=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Token refresh failed: {error_text}")
                
                return await response.json()


class SocialAuthIntegration:
    """Integration layer for social authentication with existing user management"""
    
    def __init__(self, social_auth_manager: SocialAuthManager, user_manager):
        self.social_auth = social_auth_manager
        self.user_manager = user_manager
    
    async def handle_social_login(self, provider_name: str, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Handle complete social login flow"""
        try:
            # Exchange code for token
            token_data = await self.social_auth.exchange_code_for_token(provider_name, code, state)
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise Exception("No access token received")
            
            # Get user info
            social_user = await self.social_auth.get_user_info(provider_name, access_token)
            
            # Check if user exists or create new one
            existing_user = await self.user_manager.get_user_by_social_id(provider_name, social_user.provider_id)
            
            if existing_user:
                # Update existing user's social data
                await self.user_manager.update_social_data(existing_user["id"], social_user)
                user = existing_user
            else:
                # Check if user exists by email
                email_user = await self.user_manager.get_user_by_email(social_user.email) if social_user.email else None
                
                if email_user:
                    # Link social account to existing user
                    await self.user_manager.link_social_account(email_user["id"], social_user)
                    user = email_user
                else:
                    # Create new user from social data
                    user = await self.user_manager.create_user_from_social(social_user)
            
            # Generate JWT token for the user
            jwt_token = await self.user_manager.generate_jwt_token(user)
            
            return {
                "success": True,
                "user": user,
                "token": jwt_token,
                "provider": provider_name,
                "social_data": social_user.__dict__
            }
            
        except Exception as e:
            logger.error(f"Social login failed for {provider_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": provider_name
            }
    
    async def link_social_account(self, user_id: str, provider_name: str, code: str) -> Dict[str, Any]:
        """Link a social media account to an existing user"""
        try:
            # Exchange code for token
            token_data = await self.social_auth.exchange_code_for_token(provider_name, code)
            access_token = token_data.get("access_token")
            
            # Get user info
            social_user = await self.social_auth.get_user_info(provider_name, access_token)
            
            # Link to existing user
            await self.user_manager.link_social_account(user_id, social_user)
            
            return {
                "success": True,
                "provider": provider_name,
                "linked_account": social_user.name
            }
            
        except Exception as e:
            logger.error(f"Social account linking failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unlink_social_account(self, user_id: str, provider_name: str) -> Dict[str, Any]:
        """Unlink a social media account from a user"""
        try:
            await self.user_manager.unlink_social_account(user_id, provider_name)
            return {
                "success": True,
                "provider": provider_name
            }
        except Exception as e:
            logger.error(f"Social account unlinking failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Usage example and testing
async def demo_social_auth():
    """Demonstrate social authentication functionality"""
    print("🔐 Social Media Authentication Demo")
    print("=" * 50)
    
    # Initialize social auth manager
    social_auth = SocialAuthManager()
    
    # List configured providers
    providers = social_auth.list_providers()
    print(f"📱 Configured Providers: {len(providers)}")
    for provider in providers:
        status = "[CHECK] Ready" if provider["configured"] else "[ERROR] Not configured"
        print(f"  • {provider['name']}: {status}")
    
    # Generate auth URLs (demo - these would redirect in a real app)
    print("\n🔗 Sample Authorization URLs:")
    for provider in ["google", "github", "facebook"]:
        try:
            auth_url = social_auth.get_auth_url(provider)
            print(f"  • {provider.title()}: {auth_url[:80]}...")
        except Exception as e:
            print(f"  • {provider.title()}: Not configured ({str(e)})")
    
    print("\n✨ Social authentication system ready!")
    print("Configure provider credentials in environment variables to enable.")
    
    return social_auth


if __name__ == "__main__":
    asyncio.run(demo_social_auth())
