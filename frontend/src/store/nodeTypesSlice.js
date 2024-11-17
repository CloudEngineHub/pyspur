import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getNodeTypes } from '../utils/api';

const initialState = {
  data: null,      // This will store the schema object
  metadata: null,  // This will store the metadata
  status: 'idle',
  error: null,
};

export const fetchNodeTypes = createAsyncThunk(
  'nodeTypes/fetchNodeTypes',
  async () => {
    const response = await getNodeTypes();
    return response;  // Now returns { schema, metadata }
  }
);

const nodeTypesSlice = createSlice({
  name: 'nodeTypes',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchNodeTypes.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchNodeTypes.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.data = action.payload.schema;
        state.metadata = action.payload.metadata;
      })
      .addCase(fetchNodeTypes.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

// Helper function to find metadata in the nested structure
const findMetadataInCategory = (metadata, nodeType, path) => {
  if (!metadata) return null;

  // Find which category the node belongs to
  const categories = ['primitives', 'llm', 'python'];
  for (const category of categories) {
    const nodes = metadata[category];
    if (!nodes) continue;

    // Find the node in the category
    const nodeIndex = nodes.findIndex(node => node.name === nodeType);
    if (nodeIndex === -1) continue;

    // Navigate the remaining path
    let current = nodes[nodeIndex];
    const remainingPath = path.split('.');

    for (const part of remainingPath) {
      if (!current || !current[part]) return null;
      current = current[part];
    }

    return current;
  }
  return null;
};

export const selectPropertyMetadata = (state, propertyPath) => {
  if (!propertyPath) return null;

  // Split path into nodeType and remaining path
  const [nodeType, ...pathParts] = propertyPath.split('.');
  const remainingPath = pathParts.join('.');

  return findMetadataInCategory(state.nodeTypes.metadata, nodeType, remainingPath);
};

export default nodeTypesSlice.reducer;
