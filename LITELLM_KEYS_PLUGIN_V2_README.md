# LiteLLM Keys Management Plugin V2 - API-Based Implementation

## 🎯 Overview

The **LiteLLM Keys Management Plugin V2** is a redesigned plugin for Open WebUI that provides secure API key management through LiteLLM's existing API infrastructure. This version eliminates the need for database migrations and provides enhanced security by showing API keys only once during creation.

## ✨ Key Features

### 🔒 **Enhanced Security**
- **Show Key Once**: API keys are displayed only during creation for maximum security
- **Master Key Authentication**: Uses a single master API key for all operations
- **No Database Storage**: Keys are managed entirely through LiteLLM's API
- **Real-time Status**: Always get current key status from LiteLLM API

### 🚀 **Simplified Deployment**
- **No Database Migrations**: Zero database schema changes required
- **Environment Configuration**: Simple environment variable setup
- **API-Based Architecture**: Leverages existing LiteLLM infrastructure
- **Easy Updates**: Minimal code changes for future Open WebUI updates

### 👥 **Group-Based Access Control**
- **SSO Integration**: Works with Open WebUI's existing authentication
- **Group Sharing**: Share keys with specific user groups
- **Accessible Keys Tab**: View keys shared through group membership
- **Permission-Based UI**: Respects Open WebUI's permission system

## 🏗️ Architecture

### Backend Components

#### 1. **LiteLLM Client** (`/backend/open_webui/utils/litellm_client.py`)
```python
class LiteLLMClient:
    """Client for interacting with LiteLLM API for key management."""
    
    async def create_user_key(self, user_id: str, key_name: str, groups: List[str] = None)
    async def get_user_keys(self, user_id: str) -> List[Dict[str, Any]]
    async def update_user_key(self, key_id: str, user_id: str, updates: Dict[str, Any])
    async def delete_user_key(self, key_id: str, user_id: str) -> bool
    async def get_key_status(self, key_id: str) -> Dict[str, Any]
    async def get_accessible_keys(self, user_id: str, user_groups: List[str])
```

#### 2. **API Router** (`/backend/open_webui/routers/litellm_keys_v2.py`)
- **GET** `/api/v1/litellm-keys/` - List user's keys
- **POST** `/api/v1/litellm-keys/` - Create new key (returns actual key once)
- **GET** `/api/v1/litellm-keys/{key_id}` - Get specific key
- **PUT** `/api/v1/litellm-keys/{key_id}` - Update key (no key returned)
- **DELETE** `/api/v1/litellm-keys/{key_id}` - Delete key
- **GET** `/api/v1/litellm-keys/{key_id}/status` - Get key status
- **GET** `/api/v1/litellm-keys/groups/accessible` - Get accessible keys
- **GET** `/api/v1/litellm-keys/health/connection` - Test connection (admin)

#### 3. **Configuration** (`/backend/open_webui/config.py`)
```python
# LiteLLM Configuration
LITELLM_MASTER_API_KEY = os.getenv("LITELLM_MASTER_API_KEY", "")
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_ENABLED = os.getenv("LITELLM_ENABLED", "false").lower() == "true"
```

### Frontend Components

#### 1. **API Client** (`/src/lib/apis/litellm-keys/index.ts`)
```typescript
export const createLiteLLMKey = async (token: string, keyData: LiteLLMKeyCreateForm)
export const getLiteLLMKeys = async (token: string)
export const updateLiteLLMKey = async (token: string, keyId: string, updates: LiteLLMKeyUpdateForm)
export const deleteLiteLLMKey = async (token: string, keyId: string)
export const getLiteLLMKeyStatus = async (token: string, keyId: string)
export const getAccessibleLiteLLMKeys = async (token: string)
export const testLiteLLMConnection = async (token: string)
```

#### 2. **UI Components** (`/src/routes/(app)/workspace/litellm-keys/+page.svelte`)
- **Tabbed Interface**: "My Keys" and "Accessible Keys" tabs
- **Create Key Modal**: Simple form with group selection
- **Show Key Once Modal**: Displays new key with copy functionality
- **Edit Key Modal**: Update key properties (no key shown)
- **Delete Confirmation**: Safe deletion with confirmation
- **Real-time Status**: Live key status from LiteLLM API

## 🚀 Installation

### 1. **Environment Setup**

Add these environment variables to your Open WebUI configuration:

```bash
# LiteLLM Configuration
LITELLM_MASTER_API_KEY="your_litellm_master_api_key_here"
LITELLM_BASE_URL="http://localhost:4000"  # Your LiteLLM server URL
LITELLM_ENABLED="true"
```

### 2. **Install Plugin Files**

Run the installation script:

```bash
chmod +x install_litellm_keys_plugin_v2.sh
./install_litellm_keys_plugin_v2.sh
```

### 3. **Restart Open WebUI**

```bash
# If using Docker
docker restart open-webui

# If running directly
# Restart your Open WebUI process
```

## 📋 Usage

### **Creating a New Key**

1. Navigate to **Workspace → LiteLLM Keys**
2. Click **"Add New Key"**
3. Fill in the form:
   - **Key Name**: Descriptive name for the key
   - **Groups**: Select groups that can access this key (optional)
   - **Description**: Additional details (optional)
4. Click **"Create Key"**
5. **Important**: Copy and save the API key immediately - it won't be shown again!

### **Managing Keys**

- **View Keys**: See all your keys with masked API keys
- **Edit Keys**: Update key name, groups, and description
- **Delete Keys**: Remove keys you no longer need
- **Check Status**: View real-time usage and status information
- **Accessible Keys**: View keys shared through group membership

### **Group-Based Sharing**

1. Create a key and assign it to specific groups
2. Users in those groups can access the key through the "Accessible Keys" tab
3. Keys show as "Shared" to indicate they're not owned by the current user

## 🔧 Configuration

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LITELLM_MASTER_API_KEY` | Master API key for LiteLLM operations | `""` | Yes |
| `LITELLM_BASE_URL` | LiteLLM server base URL | `http://localhost:4000` | Yes |
| `LITELLM_ENABLED` | Enable/disable LiteLLM integration | `false` | No |

### **LiteLLM Server Requirements**

Your LiteLLM server should support these API endpoints:

- `GET /key/info` - List all keys
- `POST /key/generate` - Create new key
- `PUT /key/update` - Update existing key
- `DELETE /key/delete` - Delete key
- `GET /key/info/{key_id}` - Get key details
- `GET /health` - Health check

## 🛡️ Security Features

### **Key Security**
- **Show Once**: API keys are only displayed during creation
- **Masked Display**: All other views show masked keys (e.g., `sk-1234...5678`)
- **Secure Storage**: Keys are stored in LiteLLM's secure infrastructure
- **Access Control**: Group-based permissions for key sharing

### **Authentication**
- **Master Key**: Single admin key for all operations
- **User Context**: All operations are scoped to the authenticated user
- **Group Validation**: Users can only assign keys to groups they belong to
- **Permission Checks**: Respects Open WebUI's permission system

### **Audit Trail**
- **Operation Logging**: All key operations are logged
- **User Tracking**: All actions are tied to specific users
- **Status Monitoring**: Real-time key usage and status tracking

## 🔍 API Reference

### **Create Key**
```http
POST /api/v1/litellm-keys/
Content-Type: application/json
Authorization: Bearer <user_token>

{
  "key_name": "My API Key",
  "groups": ["group1", "group2"],
  "description": "Key for production use"
}
```

**Response** (shows actual key once):
```json
{
  "id": "key_123",
  "user_id": "user_456",
  "key_name": "My API Key",
  "api_key": "sk-1234567890abcdef...",
  "groups": ["group1", "group2"],
  "is_active": true,
  "description": "Key for production use",
  "created_at": 1640995200
}
```

### **List Keys**
```http
GET /api/v1/litellm-keys/
Authorization: Bearer <user_token>
```

**Response** (keys are masked):
```json
{
  "keys": [
    {
      "id": "key_123",
      "user_id": "user_456",
      "key_name": "My API Key",
      "api_key": "sk-1234...5678",
      "groups": ["group1", "group2"],
      "is_active": true,
      "description": "Key for production use",
      "created_at": 1640995200,
      "last_used_at": 1640995800
    }
  ],
  "total": 1
}
```

### **Get Key Status**
```http
GET /api/v1/litellm-keys/{key_id}/status
Authorization: Bearer <user_token>
```

**Response**:
```json
{
  "id": "key_123",
  "is_active": true,
  "usage_count": 42,
  "last_used": "2024-01-01T12:00:00Z",
  "expires_at": null,
  "budget_used": 0.0,
  "budget_limit": null
}
```

## 🧪 Testing

### **Test Connection**
```bash
# Test LiteLLM connection (admin only)
curl -X GET "http://localhost:8080/api/v1/litellm-keys/health/connection" \
  -H "Authorization: Bearer <admin_token>"
```

### **Test Key Creation**
```bash
# Create a new key
curl -X POST "http://localhost:8080/api/v1/litellm-keys/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <user_token>" \
  -d '{
    "key_name": "Test Key",
    "description": "Testing the API"
  }'
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. "LiteLLM integration is disabled"**
- **Solution**: Set `LITELLM_ENABLED=true` in your environment

#### **2. "LiteLLM master API key is not configured"**
- **Solution**: Set `LITELLM_MASTER_API_KEY` to your LiteLLM master key

#### **3. "Failed to connect to LiteLLM API"**
- **Solution**: Check `LITELLM_BASE_URL` and ensure LiteLLM server is running

#### **4. "Access denied to LiteLLM key management"**
- **Solution**: Ensure user has proper permissions in Open WebUI

### **Debug Mode**

Enable debug logging by setting:
```bash
SRC_LOG_LEVELS="LITELLM_CLIENT=DEBUG"
```

## 🔄 Migration from V1

If you're upgrading from the database-based V1 plugin:

1. **Backup your data** (if you have existing keys in the database)
2. **Install V2** using the new installation script
3. **Configure environment variables** for LiteLLM connection
4. **Test the connection** using the health endpoint
5. **Recreate keys** through the new interface (keys from V1 won't be accessible)

## 📈 Benefits of V2

### **For Administrators**
- ✅ **No Database Changes**: Zero migration complexity
- ✅ **Centralized Management**: All keys managed through LiteLLM
- ✅ **Better Security**: Master key authentication
- ✅ **Easier Updates**: Minimal code changes for Open WebUI updates

### **For Users**
- ✅ **Enhanced Security**: Keys shown only once
- ✅ **Real-time Status**: Always current information
- ✅ **Group Sharing**: Easy collaboration through groups
- ✅ **Better UX**: Cleaner, more intuitive interface

### **For Developers**
- ✅ **API-Based**: Leverages existing LiteLLM infrastructure
- ✅ **Isolated Code**: Easy to maintain and update
- ✅ **Comprehensive Logging**: Better debugging and monitoring
- ✅ **Type Safety**: Full TypeScript support

## 🤝 Contributing

This plugin is designed to be easily maintainable and extensible:

1. **Backend**: Add new endpoints in `litellm_keys_v2.py`
2. **Frontend**: Extend the UI in `+page.svelte`
3. **API Client**: Add new functions in `index.ts`
4. **Documentation**: Update this README for new features

## 📄 License

This plugin follows the same license as Open WebUI.

## 🆘 Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Review the logs** for error details
3. **Test the connection** using the health endpoint
4. **Verify environment variables** are correctly set

---

**LiteLLM Keys Management Plugin V2** - Secure, API-based key management for Open WebUI 🚀