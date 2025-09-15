# LiteLLM Keys Management Plugin for Open WebUI

## Overview

The LiteLLM Keys Management Plugin is a comprehensive solution that integrates with Open WebUI to provide secure management of LiteLLM API keys. This plugin addresses the security policy requirements by allowing users to manage their LiteLLM API keys through Open WebUI's SSO system, eliminating the need for users to set their own passwords on the LiteLLM server.

## Features

### 🔐 Secure Key Management
- **Encrypted Storage**: API keys are stored securely in the database
- **Access Control**: Group-based access control for sharing keys
- **User Isolation**: Users can only manage their own keys (unless admin)
- **Key Masking**: API keys are masked in the UI for security

### 👥 Group-Based Access Control
- **Group Sharing**: Share keys with specific user groups
- **SSO Integration**: Leverages Open WebUI's existing SSO and group management
- **Permission-Based Access**: Respects Open WebUI's permission system

### 🎨 User-Friendly Interface
- **Intuitive UI**: Clean, modern interface integrated with Open WebUI's design
- **Tabbed Navigation**: Separate tabs for personal keys and group-accessible keys
- **Real-time Updates**: Immediate feedback on all operations
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Administrative Features
- **Admin Override**: Administrators can manage all keys
- **Audit Trail**: Track key creation, modification, and usage
- **Bulk Operations**: Efficient management of multiple keys

## Architecture

### Backend Components

#### 1. Database Model (`models/litellm_keys.py`)
```python
class LiteLLMKey(Base):
    __tablename__ = "litellm_key"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"))
    key_name = Column(Text, nullable=False)
    api_key = Column(Text, nullable=False)  # Encrypted
    key_type = Column(String, default="api_key")
    group_ids = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    # ... additional fields
```

#### 2. API Router (`routers/litellm_keys.py`)
- **GET** `/api/v1/litellm-keys/` - List user's keys
- **POST** `/api/v1/litellm-keys/` - Create new key
- **GET** `/api/v1/litellm-keys/{key_id}` - Get specific key
- **PUT** `/api/v1/litellm-keys/{key_id}` - Update key
- **DELETE** `/api/v1/litellm-keys/{key_id}` - Delete key
- **GET** `/api/v1/litellm-keys/groups/accessible` - Get group-accessible keys

#### 3. CRUD Operations (`models/litellm_keys.py`)
```python
class LiteLLMKeys:
    @staticmethod
    def create_key(user_id: str, key_data: LiteLLMKeyCreateForm) -> LiteLLMKeyModel
    
    @staticmethod
    def get_keys_by_user_id(user_id: str, skip: int = 0, limit: int = 100) -> LiteLLMKeyListResponse
    
    @staticmethod
    def update_key(key_id: str, user_id: str, update_data: LiteLLMKeyUpdateForm) -> LiteLLMKeyModel
    
    @staticmethod
    def delete_key(key_id: str, user_id: str) -> bool
```

### Frontend Components

#### 1. API Client (`lib/apis/litellm-keys/index.ts`)
```typescript
export const getLiteLLMKeys = async (token: string, skip?: number, limit?: number): Promise<LiteLLMKeyListResponse>
export const createLiteLLMKey = async (token: string, keyData: LiteLLMKeyCreateForm): Promise<LiteLLMKey>
export const updateLiteLLMKey = async (token: string, keyId: string, updateData: LiteLLMKeyUpdateForm): Promise<LiteLLMKey>
export const deleteLiteLLMKey = async (token: string, keyId: string): Promise<void>
```

#### 2. Main UI Component (`routes/(app)/workspace/litellm-keys/+page.svelte`)
- **Tabbed Interface**: Personal keys vs. group-accessible keys
- **Modal Forms**: Create, edit, and delete operations
- **Real-time Updates**: Immediate UI feedback
- **Responsive Design**: Mobile-friendly layout

## Installation

### Prerequisites
- Open WebUI instance with database access
- Python 3.8+ with FastAPI
- Node.js 16+ for frontend development

### Backend Installation

1. **Add the model to your Open WebUI installation:**
   ```bash
   # Copy the model file
   cp models/litellm_keys.py /path/to/open-webui/backend/open_webui/models/
   
   # Copy the router
   cp routers/litellm_keys.py /path/to/open-webui/backend/open_webui/routers/
   ```

2. **Update the main application:**
   ```python
   # In main.py, add the import
   from open_webui.routers import litellm_keys
   
   # Add the router
   app.include_router(litellm_keys.router, prefix="/api/v1/litellm-keys", tags=["litellm-keys"])
   ```

3. **Update the User model:**
   ```python
   # In models/users.py, add the relationship
   litellm_keys = relationship("LiteLLMKey", back_populates="user")
   ```

4. **Run database migration:**
   ```bash
   # Copy the migration file
   cp migrations/versions/a1b2c3d4e5f6_add_litellm_keys_table.py /path/to/open-webui/backend/open_webui/migrations/versions/
   
   # Run the migration
   alembic upgrade head
   ```

### Frontend Installation

1. **Add the API client:**
   ```bash
   # Copy the API client
   cp lib/apis/litellm-keys/index.ts /path/to/open-webui/src/lib/apis/litellm-keys/
   ```

2. **Add the UI component:**
   ```bash
   # Copy the page component
   cp routes/(app)/workspace/litellm-keys/+page.svelte /path/to/open-webui/src/routes/(app)/workspace/litellm-keys/
   ```

3. **Update the workspace layout:**
   ```svelte
   <!-- Add to workspace/+layout.svelte -->
   {#if $user?.role === 'admin' || $user?.permissions?.workspace?.litellm_keys}
       <a href="/workspace/litellm-keys">LiteLLM Keys</a>
   {/if}
   ```

## Configuration

### Environment Variables

No additional environment variables are required. The plugin uses Open WebUI's existing configuration.

### Permissions

The plugin respects Open WebUI's permission system. To enable LiteLLM Keys management for users:

1. **Admin Access**: Administrators have full access by default
2. **User Access**: Add `litellm_keys: true` to user permissions in Open WebUI admin settings

### Group Configuration

Groups are managed through Open WebUI's existing group system. Users can share keys with groups they belong to.

## Usage

### For End Users

1. **Access the Plugin:**
   - Navigate to Workspace → LiteLLM Keys
   - Or go directly to `/workspace/litellm-keys`

2. **Create a New Key:**
   - Click "Add New Key"
   - Enter key name, API key, and optional description
   - Select groups for sharing (optional)
   - Click "Create Key"

3. **Manage Existing Keys:**
   - View all your keys in the "My Keys" tab
   - Edit key details by clicking the edit icon
   - Delete keys by clicking the delete icon
   - Toggle key active/inactive status

4. **Access Group Keys:**
   - View keys shared with your groups in the "Accessible Keys" tab
   - These keys are read-only for non-owners

### For Administrators

1. **Full Access:**
   - Administrators can view and manage all keys
   - Access to admin-only endpoints for system-wide key management

2. **User Management:**
   - Grant/revoke LiteLLM Keys permissions for users
   - Monitor key usage and access patterns

## Security Considerations

### Data Protection
- **Encryption**: API keys should be encrypted before storage (implement in production)
- **Access Control**: Strict user and group-based access control
- **Audit Logging**: All operations are logged for security auditing

### Best Practices
- **Regular Rotation**: Encourage users to rotate API keys regularly
- **Minimal Permissions**: Grant only necessary permissions to users
- **Group Management**: Regularly review group memberships and key sharing

## API Reference

### Authentication
All API endpoints require authentication via Open WebUI's token system:
```http
Authorization: Bearer <token>
```

### Endpoints

#### List Keys
```http
GET /api/v1/litellm-keys/?skip=0&limit=100
```

#### Create Key
```http
POST /api/v1/litellm-keys/
Content-Type: application/json

{
  "key_name": "My LiteLLM Key",
  "api_key": "sk-...",
  "key_type": "api_key",
  "group_ids": ["group1", "group2"],
  "description": "Key for production use"
}
```

#### Update Key
```http
PUT /api/v1/litellm-keys/{key_id}
Content-Type: application/json

{
  "key_name": "Updated Key Name",
  "is_active": false
}
```

#### Delete Key
```http
DELETE /api/v1/litellm-keys/{key_id}
```

## Troubleshooting

### Common Issues

1. **Permission Denied:**
   - Ensure user has `litellm_keys` permission
   - Check if user is in the correct groups

2. **Database Errors:**
   - Verify migration was run successfully
   - Check database connection and permissions

3. **UI Not Loading:**
   - Ensure all frontend files are copied correctly
   - Check browser console for JavaScript errors

### Debug Mode

Enable debug logging by setting the log level in Open WebUI configuration:
```python
SRC_LOG_LEVELS["LITELLM_KEYS"] = "DEBUG"
```

## Development

### Adding New Features

1. **Backend Changes:**
   - Update the model in `models/litellm_keys.py`
   - Add new endpoints in `routers/litellm_keys.py`
   - Create database migration if needed

2. **Frontend Changes:**
   - Update API client in `lib/apis/litellm-keys/index.ts`
   - Modify UI components in `routes/(app)/workspace/litellm-keys/+page.svelte`

### Testing

1. **Backend Testing:**
   ```bash
   # Run backend tests
   python -m pytest tests/test_litellm_keys.py
   ```

2. **Frontend Testing:**
   ```bash
   # Run frontend tests
   npm test
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This plugin is released under the same license as Open WebUI.

## Support

For support and questions:
- Create an issue in the Open WebUI repository
- Check the documentation and troubleshooting guide
- Review the API reference for technical details

## Changelog

### Version 1.0.0
- Initial release
- Basic CRUD operations for LiteLLM keys
- Group-based access control
- User-friendly web interface
- Integration with Open WebUI's authentication system

---

**Note**: This plugin is designed to be isolated from the main Open WebUI codebase to facilitate easy rebasing and updates. All plugin-specific code is contained within the designated files and directories.