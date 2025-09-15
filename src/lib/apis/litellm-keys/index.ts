/**
 * LiteLLM Keys API
 * 
 * This module provides API functions for managing LiteLLM API keys in Open WebUI.
 * It includes functionality for creating, reading, updating, and deleting API keys
 * with proper authentication and access control.
 * 
 * Author: LiteLLM Key Management Plugin
 */

import { WEBUI_API_BASE_URL } from '$lib/constants';

// Types
export interface LiteLLMKey {
	id: string;
	user_id: string;
	key_name: string;
	api_key: string; // This will be masked in responses
	key_type: string;
	group_ids?: string[];
	is_active: boolean;
	description?: string;
	metadata?: Record<string, any>;
	created_at: number;
	updated_at: number;
	last_used_at?: number;
}

export interface LiteLLMKeyCreateForm {
	key_name: string;
	api_key: string;
	key_type?: string;
	group_ids?: string[];
	description?: string;
	metadata?: Record<string, any>;
}

export interface LiteLLMKeyUpdateForm {
	key_name?: string;
	api_key?: string;
	key_type?: string;
	group_ids?: string[];
	is_active?: boolean;
	description?: string;
	metadata?: Record<string, any>;
}

export interface LiteLLMKeyListResponse {
	keys: LiteLLMKey[];
	total: number;
}

// API Functions

/**
 * Get all LiteLLM keys for the authenticated user
 */
export const getLiteLLMKeys = async (
	token: string,
	skip: number = 0,
	limit: number = 100
): Promise<LiteLLMKeyListResponse> => {
	let error = null;

	const searchParams = new URLSearchParams();
	searchParams.set('skip', skip.toString());
	searchParams.set('limit', limit.toString());

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/?${searchParams.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Get a specific LiteLLM key by ID
 */
export const getLiteLLMKey = async (token: string, keyId: string): Promise<LiteLLMKey> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/${keyId}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Create a new LiteLLM key
 */
export const createLiteLLMKey = async (
	token: string,
	keyData: LiteLLMKeyCreateForm
): Promise<LiteLLMKey> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(keyData)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Update an existing LiteLLM key
 */
export const updateLiteLLMKey = async (
	token: string,
	keyId: string,
	updateData: LiteLLMKeyUpdateForm
): Promise<LiteLLMKey> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/${keyId}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(updateData)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Delete a LiteLLM key
 */
export const deleteLiteLLMKey = async (token: string, keyId: string): Promise<void> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/${keyId}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Get LiteLLM keys accessible through user's groups
 */
export const getAccessibleLiteLLMKeys = async (token: string): Promise<LiteLLMKey[]> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/litellm-keys/groups/accessible`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Utility function to mask API key for display
 */
export const maskApiKey = (apiKey: string): string => {
	if (apiKey.length <= 12) {
		return '*'.repeat(apiKey.length);
	}
	return apiKey.substring(0, 8) + '*'.repeat(apiKey.length - 12) + apiKey.substring(apiKey.length - 4);
};

/**
 * Utility function to validate API key format
 */
export const validateApiKey = (apiKey: string): boolean => {
	// Basic validation - can be extended based on LiteLLM key format requirements
	return apiKey && apiKey.trim().length > 0;
};

/**
 * Utility function to validate key name
 */
export const validateKeyName = (keyName: string): boolean => {
	// Basic validation - key name should not be empty and should be reasonable length
	return keyName && keyName.trim().length > 0 && keyName.trim().length <= 100;
};