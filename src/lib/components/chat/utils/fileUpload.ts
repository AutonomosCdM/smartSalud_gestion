/**
 * File upload utilities extracted from Chat.svelte
 * These functions handle Google Drive, web URL, and YouTube uploads
 */

import { v4 as uuidv4 } from 'uuid';
import { uploadFile } from '$lib/apis/files';
import { processWeb, processYoutubeVideo } from '$lib/apis/retrieval';
import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface FileItem {
	type: 'file' | 'text';
	file?: any;
	id?: string | null;
	url?: string;
	name: string;
	collection_name: string;
	status: 'uploading' | 'uploaded' | 'error';
	error: string;
	itemId?: string;
	size?: number;
	context?: string;
}

export interface GoogleDriveFileData {
	id: string;
	name: string;
	url: string;
	headers: {
		Authorization: string;
	};
}

export interface UploadResult {
	success: boolean;
	fileItem?: FileItem;
	error?: string;
}

/**
 * Upload a file from Google Drive
 */
export const uploadGoogleDriveFile = async (
	fileData: GoogleDriveFileData,
	token: string,
	sttLanguage?: string
): Promise<UploadResult> => {
	console.log('Starting uploadGoogleDriveFile with:', {
		id: fileData.id,
		name: fileData.name,
		url: fileData.url
	});

	// Validate input
	if (!fileData?.id || !fileData?.name || !fileData?.url || !fileData?.headers?.Authorization) {
		return { success: false, error: 'Invalid file data provided' };
	}

	const tempItemId = uuidv4();
	const fileItem: FileItem = {
		type: 'file',
		file: '',
		id: null,
		url: fileData.url,
		name: fileData.name,
		collection_name: '',
		status: 'uploading',
		error: '',
		itemId: tempItemId,
		size: 0
	};

	try {
		// Configure fetch options with proper headers
		const fetchOptions = {
			headers: {
				Authorization: fileData.headers.Authorization,
				Accept: '*/*'
			},
			method: 'GET'
		};

		// Attempt to fetch the file
		console.log('Fetching file content from Google Drive...');
		const fileResponse = await fetch(fileData.url, fetchOptions);

		if (!fileResponse.ok) {
			const errorText = await fileResponse.text();
			return { success: false, error: `Failed to fetch file (${fileResponse.status}): ${errorText}` };
		}

		// Get content type from response
		const contentType = fileResponse.headers.get('content-type') || 'application/octet-stream';
		console.log('Response received with content-type:', contentType);

		// Convert response to blob
		const fileBlob = await fileResponse.blob();

		if (fileBlob.size === 0) {
			return { success: false, error: 'Retrieved file is empty' };
		}

		// Create File object with proper MIME type
		const file = new File([fileBlob], fileData.name, {
			type: fileBlob.type || contentType
		});

		if (file.size === 0) {
			return { success: false, error: 'Created file is empty' };
		}

		// If the file is an audio file, provide the language for STT
		let metadata = null;
		if ((file.type.startsWith('audio/') || file.type.startsWith('video/')) && sttLanguage) {
			metadata = { language: sttLanguage };
		}

		// Upload file to server
		console.log('Uploading file to server...');
		const uploadedFile = await uploadFile(token, file, metadata);

		if (!uploadedFile) {
			return { success: false, error: 'Server returned null response for file upload' };
		}

		console.log('File uploaded successfully:', uploadedFile);

		// Update file item with upload results
		fileItem.status = 'uploaded';
		fileItem.file = uploadedFile;
		fileItem.id = uploadedFile.id;
		fileItem.size = file.size;
		fileItem.collection_name = uploadedFile?.meta?.collection_name;
		fileItem.url = `${WEBUI_API_BASE_URL}/files/${uploadedFile.id}`;

		return { success: true, fileItem };
	} catch (e: any) {
		console.error('Error uploading file:', e);
		return { success: false, error: e.message || 'Unknown error' };
	}
};

/**
 * Upload content from a web URL
 */
export const uploadWebUrl = async (
	url: string,
	token: string
): Promise<UploadResult> => {
	console.log('Uploading web URL:', url);

	const fileItem: FileItem = {
		type: 'text',
		name: url,
		collection_name: '',
		status: 'uploading',
		url: url,
		error: ''
	};

	try {
		const res = await processWeb(token, '', url);

		if (res) {
			fileItem.status = 'uploaded';
			fileItem.collection_name = res.collection_name;
			fileItem.file = {
				...res.file,
				...fileItem.file
			};
			return { success: true, fileItem };
		}

		return { success: false, error: 'No response from server' };
	} catch (e: any) {
		console.error('Error uploading web URL:', e);
		return { success: false, error: JSON.stringify(e) };
	}
};

/**
 * Upload YouTube video transcription
 */
export const uploadYoutubeTranscription = async (
	url: string,
	token: string
): Promise<UploadResult> => {
	console.log('Uploading YouTube transcription:', url);

	const fileItem: FileItem = {
		type: 'text',
		name: url,
		collection_name: '',
		status: 'uploading',
		context: 'full',
		url: url,
		error: ''
	};

	try {
		const res = await processYoutubeVideo(token, url);

		if (res) {
			fileItem.status = 'uploaded';
			fileItem.collection_name = res.collection_name;
			fileItem.file = {
				...res.file,
				...fileItem.file
			};
			return { success: true, fileItem };
		}

		return { success: false, error: 'No response from server' };
	} catch (e: any) {
		console.error('Error uploading YouTube transcription:', e);
		return { success: false, error: String(e) };
	}
};
