<!--
	LiteLLM Keys Management Page V2 - API-Based Implementation
	
	This page provides a user interface for managing LiteLLM API keys through
	LiteLLM's existing API, eliminating the need for database storage.
	Keys are shown only once during creation for security.
	
	Author: LiteLLM Key Management Plugin
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { fade, fly } from 'svelte/transition';
	import { getContext } from 'svelte';

	import {
		getLiteLLMKeys,
		createLiteLLMKey,
		updateLiteLLMKey,
		deleteLiteLLMKey,
		getAccessibleLiteLLMKeys,
		getLiteLLMKeyStatus,
		testLiteLLMConnection,
		type LiteLLMKey,
		type LiteLLMKeyCreateForm,
		type LiteLLMKeyUpdateForm,
		maskApiKey,
		validateKeyName
	} from '$lib/apis/litellm-keys';
	import { getUserGroups } from '$lib/apis/users';
	import type { Group } from '$lib/types';

	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import Select from '$lib/components/common/Select.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Card from '$lib/components/common/Card.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Icon from '$lib/components/common/Icon.svelte';

	const i18n = getContext('i18n');

	// State
	let keys: LiteLLMKey[] = [];
	let accessibleKeys: LiteLLMKey[] = [];
	let groups: Group[] = [];
	let loading = true;
	let error: string | null = null;

	// Modal state
	let showCreateModal = false;
	let showEditModal = false;
	let showDeleteModal = false;
	let showNewKeyModal = false;
	let selectedKey: LiteLLMKey | null = null;

	// Form state
	let createForm: LiteLLMKeyCreateForm = {
		key_name: '',
		groups: [],
		description: ''
	};

	let editForm: LiteLLMKeyUpdateForm = {
		key_name: '',
		groups: [],
		description: ''
	};

	// State for showing key once
	let newKeyValue = '';
	let newKeyName = '';

	// Tab state
	let activeTab: 'my-keys' | 'accessible-keys' = 'my-keys';

	// Load data on mount
	onMount(async () => {
		await loadData();
	});

	const loadData = async () => {
		loading = true;
		error = null;

		try {
			const token = localStorage.getItem('token');
			if (!token) {
				throw new Error('No authentication token found');
			}

			// Load user's own keys
			const keysResponse = await getLiteLLMKeys(token);
			keys = keysResponse.keys;

			// Load accessible keys through groups
			accessibleKeys = await getAccessibleLiteLLMKeys(token);

			// Load user groups for form
			groups = await getUserGroups(token);

		} catch (err: any) {
			console.error('Error loading LiteLLM keys:', err);
			error = err.message || 'Failed to load LiteLLM keys';
			toast.error(error);
		} finally {
			loading = false;
		}
	};

	const handleCreateKey = async () => {
		try {
			// Validate form
			if (!validateKeyName(createForm.key_name)) {
				toast.error('Please enter a valid key name');
				return;
			}

			const token = localStorage.getItem('token');
			if (!token) {
				throw new Error('No authentication token found');
			}

			const newKey = await createLiteLLMKey(token, createForm);
			toast.success('LiteLLM key created successfully');
			
			// Show the key once
			newKeyValue = newKey.api_key;
			newKeyName = newKey.key_name;
			showNewKeyModal = true;
			
			// Reset form and close modal
			createForm = {
				key_name: '',
				groups: [],
				description: ''
			};
			showCreateModal = false;

			// Reload data
			await loadData();

		} catch (err: any) {
			console.error('Error creating LiteLLM key:', err);
			toast.error(err.message || 'Failed to create LiteLLM key');
		}
	};

	const handleEditKey = async () => {
		if (!selectedKey) return;

		try {
			const token = localStorage.getItem('token');
			if (!token) {
				throw new Error('No authentication token found');
			}

			await updateLiteLLMKey(token, selectedKey.id, editForm);
			toast.success('LiteLLM key updated successfully');
			
			showEditModal = false;
			selectedKey = null;

			// Reload data
			await loadData();

		} catch (err: any) {
			console.error('Error updating LiteLLM key:', err);
			toast.error(err.message || 'Failed to update LiteLLM key');
		}
	};

	const handleDeleteKey = async () => {
		if (!selectedKey) return;

		try {
			const token = localStorage.getItem('token');
			if (!token) {
				throw new Error('No authentication token found');
			}

			await deleteLiteLLMKey(token, selectedKey.id);
			toast.success('LiteLLM key deleted successfully');
			
			showDeleteModal = false;
			selectedKey = null;

			// Reload data
			await loadData();

		} catch (err: any) {
			console.error('Error deleting LiteLLM key:', err);
			toast.error(err.message || 'Failed to delete LiteLLM key');
		}
	};

	const openEditModal = (key: LiteLLMKey) => {
		selectedKey = key;
		editForm = {
			key_name: key.key_name,
			groups: key.groups || [],
			description: key.description || ''
		};
		showEditModal = true;
	};

	const openDeleteModal = (key: LiteLLMKey) => {
		selectedKey = key;
		showDeleteModal = true;
	};

	const formatDate = (timestamp: number) => {
		return new Date(timestamp * 1000).toLocaleString();
	};

	const getGroupNames = (groupIds: string[] | undefined) => {
		if (!groupIds || groupIds.length === 0) return [];
		return groupIds.map(id => groups.find(g => g.id === id)?.name || id);
	};

	const copyToClipboard = async (text: string) => {
		try {
			await navigator.clipboard.writeText(text);
			toast.success('Copied to clipboard');
		} catch (err) {
			toast.error('Failed to copy to clipboard');
		}
	};
</script>

<svelte:head>
	<title>LiteLLM Keys - Open WebUI</title>
</svelte:head>

<div class="flex flex-col h-full">
	<!-- Header -->
	<div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
		<div>
			<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
				LiteLLM Keys Management
			</h1>
			<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
				Manage your LiteLLM API keys through LiteLLM's API
			</p>
		</div>
		<Button
			on:click={() => (showCreateModal = true)}
			class="bg-blue-600 hover:bg-blue-700 text-white"
		>
			<Icon name="plus" class="w-4 h-4 mr-2" />
			Add New Key
		</Button>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-hidden">
		{#if loading}
			<div class="flex items-center justify-center h-full">
				<Spinner className="w-8 h-8" />
			</div>
		{:else if error}
			<div class="flex items-center justify-center h-full">
				<div class="text-center">
					<Icon name="alert-circle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
					<p class="text-red-600 dark:text-red-400 mb-4">{error}</p>
					<Button on:click={loadData} class="bg-blue-600 hover:bg-blue-700 text-white">
						Try Again
					</Button>
				</div>
			</div>
		{:else}
			<!-- Tabs -->
			<div class="border-b border-gray-200 dark:border-gray-700">
				<nav class="flex space-x-8 px-6">
					<button
						class="py-4 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'my-keys'
							? 'border-blue-500 text-blue-600 dark:text-blue-400'
							: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
						on:click={() => (activeTab = 'my-keys')}
					>
						My Keys ({keys.length})
					</button>
					<button
						class="py-4 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'accessible-keys'
							? 'border-blue-500 text-blue-600 dark:text-blue-400'
							: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
						on:click={() => (activeTab = 'accessible-keys')}
					>
						Accessible Keys ({accessibleKeys.length})
					</button>
				</nav>
			</div>

			<!-- Keys List -->
			<div class="flex-1 overflow-auto p-6">
				{#if activeTab === 'my-keys'}
					{#if keys.length === 0}
						<div class="text-center py-12">
							<Icon name="key" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
							<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
								No LiteLLM keys found
							</h3>
							<p class="text-gray-600 dark:text-gray-400 mb-6">
								Create your first LiteLLM API key to get started
							</p>
							<Button
								on:click={() => (showCreateModal = true)}
								class="bg-blue-600 hover:bg-blue-700 text-white"
							>
								<Icon name="plus" class="w-4 h-4 mr-2" />
								Add New Key
							</Button>
						</div>
					{:else}
						<div class="grid gap-4">
							{#each keys as key (key.id)}
								<Card class="p-6" in:fly={{ y: 20, duration: 200 }}>
									<div class="flex items-start justify-between">
										<div class="flex-1">
											<div class="flex items-center gap-3 mb-2">
												<h3 class="text-lg font-medium text-gray-900 dark:text-white">
													{key.key_name}
												</h3>
												<Badge class={key.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}>
													{key.is_active ? 'Active' : 'Inactive'}
												</Badge>
											</div>
											
											<div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
												<div class="flex items-center gap-2">
													<Icon name="key" class="w-4 h-4" />
													<span class="font-mono">{maskApiKey(key.api_key)}</span>
													<button
														on:click={() => copyToClipboard(maskApiKey(key.api_key))}
														class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
													>
														<Icon name="copy" class="w-3 h-3" />
													</button>
												</div>
												
												{#if key.description}
													<div class="flex items-center gap-2">
														<Icon name="file-text" class="w-4 h-4" />
														<span>{key.description}</span>
													</div>
												{/if}
												
												{#if key.groups && key.groups.length > 0}
													<div class="flex items-center gap-2">
														<Icon name="users" class="w-4 h-4" />
														<span>Groups: {getGroupNames(key.groups).join(', ')}</span>
													</div>
												{/if}
												
												<div class="flex items-center gap-2">
													<Icon name="calendar" class="w-4 h-4" />
													<span>Created: {formatDate(key.created_at)}</span>
												</div>
												
												{#if key.last_used_at}
													<div class="flex items-center gap-2">
														<Icon name="clock" class="w-4 h-4" />
														<span>Last used: {formatDate(key.last_used_at)}</span>
													</div>
												{/if}
											</div>
										</div>
										
										<div class="flex items-center gap-2 ml-4">
											<Button
												on:click={() => openEditModal(key)}
												class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
												variant="ghost"
												size="sm"
											>
												<Icon name="edit" class="w-4 h-4" />
											</Button>
											<Button
												on:click={() => openDeleteModal(key)}
												class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
												variant="ghost"
												size="sm"
											>
												<Icon name="trash" class="w-4 h-4" />
											</Button>
										</div>
									</div>
								</Card>
							{/each}
						</div>
					{/if}
				{:else}
					{#if accessibleKeys.length === 0}
						<div class="text-center py-12">
							<Icon name="users" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
							<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
								No accessible keys found
							</h3>
							<p class="text-gray-600 dark:text-gray-400">
								You don't have access to any LiteLLM keys through group membership
							</p>
						</div>
					{:else}
						<div class="grid gap-4">
							{#each accessibleKeys as key (key.id)}
								<Card class="p-6" in:fly={{ y: 20, duration: 200 }}>
									<div class="flex items-start justify-between">
										<div class="flex-1">
											<div class="flex items-center gap-3 mb-2">
												<h3 class="text-lg font-medium text-gray-900 dark:text-white">
													{key.key_name}
												</h3>
												<Badge class={key.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}>
													{key.is_active ? 'Active' : 'Inactive'}
												</Badge>
												<Badge class="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
													Shared
												</Badge>
											</div>
											
											<div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
												<div class="flex items-center gap-2">
													<Icon name="key" class="w-4 h-4" />
													<span class="font-mono">{maskApiKey(key.api_key)}</span>
													<button
														on:click={() => copyToClipboard(maskApiKey(key.api_key))}
														class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
													>
														<Icon name="copy" class="w-3 h-3" />
													</button>
												</div>
												
												{#if key.description}
													<div class="flex items-center gap-2">
														<Icon name="file-text" class="w-4 h-4" />
														<span>{key.description}</span>
													</div>
												{/if}
												
												{#if key.groups && key.groups.length > 0}
													<div class="flex items-center gap-2">
														<Icon name="users" class="w-4 h-4" />
														<span>Groups: {getGroupNames(key.groups).join(', ')}</span>
													</div>
												{/if}
												
												<div class="flex items-center gap-2">
													<Icon name="calendar" class="w-4 h-4" />
													<span>Created: {formatDate(key.created_at)}</span>
												</div>
												
												{#if key.last_used_at}
													<div class="flex items-center gap-2">
														<Icon name="clock" class="w-4 h-4" />
														<span>Last used: {formatDate(key.last_used_at)}</span>
													</div>
												{/if}
											</div>
										</div>
									</div>
								</Card>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		{/if}
	</div>
</div>

<!-- Create Key Modal -->
<Modal bind:show={showCreateModal} title="Create New LiteLLM Key">
	<div class="space-y-4">
		<Input
			bind:value={createForm.key_name}
			label="Key Name"
			placeholder="Enter a name for this key"
			required
		/>
		
		<Select
			bind:value={createForm.groups}
			label="Groups (Optional)"
			placeholder="Select groups that can access this key"
			options={groups.map(g => ({ value: g.id, label: g.name }))}
			multiple
		/>
		
		<Textarea
			bind:value={createForm.description}
			label="Description (Optional)"
			placeholder="Enter a description for this key"
			rows={2}
		/>
	</div>
	
	<div class="flex justify-end gap-3 mt-6">
		<Button
			on:click={() => (showCreateModal = false)}
			variant="ghost"
		>
			Cancel
		</Button>
		<Button
			on:click={handleCreateKey}
			class="bg-blue-600 hover:bg-blue-700 text-white"
		>
			Create Key
		</Button>
	</div>
</Modal>

<!-- Edit Key Modal -->
<Modal bind:show={showEditModal} title="Edit LiteLLM Key">
	{#if selectedKey}
		<div class="space-y-4">
			<Input
				bind:value={editForm.key_name}
				label="Key Name"
				placeholder="Enter a name for this key"
				required
			/>
			
			<Select
				bind:value={editForm.groups}
				label="Groups (Optional)"
				placeholder="Select groups that can access this key"
				options={groups.map(g => ({ value: g.id, label: g.name }))}
				multiple
			/>
			
			<Textarea
				bind:value={editForm.description}
				label="Description (Optional)"
				placeholder="Enter a description for this key"
				rows={2}
			/>
			
			<div class="flex items-center gap-2">
				<input
					type="checkbox"
					id="is_active"
					bind:checked={editForm.is_active}
					class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
				/>
				<label for="is_active" class="text-sm font-medium text-gray-700 dark:text-gray-300">
					Active
				</label>
			</div>
		</div>
		
		<div class="flex justify-end gap-3 mt-6">
			<Button
				on:click={() => (showEditModal = false)}
				variant="ghost"
			>
				Cancel
			</Button>
			<Button
				on:click={handleEditKey}
				class="bg-blue-600 hover:bg-blue-700 text-white"
			>
				Update Key
			</Button>
		</div>
	{/if}
</Modal>

<!-- Delete Key Modal -->
<Modal bind:show={showDeleteModal} title="Delete LiteLLM Key">
	{#if selectedKey}
		<div class="space-y-4">
			<div class="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
				<Icon name="alert-triangle" class="w-6 h-6 text-red-600 dark:text-red-400" />
				<div>
					<h3 class="font-medium text-red-800 dark:text-red-200">
						Are you sure you want to delete this key?
					</h3>
					<p class="text-sm text-red-600 dark:text-red-400 mt-1">
						This action cannot be undone. The key "{selectedKey.key_name}" will be permanently deleted.
					</p>
				</div>
			</div>
		</div>
		
		<div class="flex justify-end gap-3 mt-6">
			<Button
				on:click={() => (showDeleteModal = false)}
				variant="ghost"
			>
				Cancel
			</Button>
			<Button
				on:click={handleDeleteKey}
				class="bg-red-600 hover:bg-red-700 text-white"
			>
				Delete Key
			</Button>
		</div>
	{/if}
</Modal>

<!-- Show New Key Modal (Key shown only once) -->
<Modal bind:show={showNewKeyModal} title="New LiteLLM Key Created">
	<div class="space-y-4">
		<div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
			<div class="flex items-center gap-3">
				<Icon name="alert-triangle" class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
				<div>
					<h3 class="font-medium text-yellow-800 dark:text-yellow-200">
						Important: Save Your API Key
					</h3>
					<p class="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
						This is the only time you will see your API key. Please copy and save it securely.
					</p>
				</div>
			</div>
		</div>
		
		<div class="space-y-3">
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Key Name
				</label>
				<div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border">
					<span class="font-medium text-gray-900 dark:text-white">{newKeyName}</span>
				</div>
			</div>
			
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					API Key
				</label>
				<div class="relative">
					<input
						type="text"
						value={newKeyValue}
						readonly
						class="w-full p-3 pr-12 bg-gray-50 dark:bg-gray-800 rounded-lg border font-mono text-sm"
						id="new-api-key"
					/>
					<button
						type="button"
						class="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
						on:click={() => copyToClipboard(newKeyValue)}
					>
						<Icon name="copy" class="w-4 h-4" />
					</button>
				</div>
			</div>
		</div>
	</div>
	
	<div class="flex justify-end gap-3 mt-6">
		<Button
			on:click={() => {
				showNewKeyModal = false;
				newKeyValue = '';
				newKeyName = '';
			}}
			class="bg-blue-600 hover:bg-blue-700 text-white"
		>
			I've Saved My Key
		</Button>
	</div>
</Modal>