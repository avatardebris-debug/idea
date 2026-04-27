import { useState, useEffect } from 'react';
import { api, type Field, type FieldCreate, type Table } from '../api';

export default function Fields() {
  const [tableId, setTableId] = useState<string | null>(null);
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState<'TEXT' | 'NUMBER' | 'DATE' | 'URL' | 'SELECT' | 'TAGS'>('TEXT');
  const [isCreating, setIsCreating] = useState(false);
  const [tables, setTables] = useState<Table[]>([]);

  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      const tablesData = await api.tables.list();
      setTables(tablesData);
      if (tablesData.length > 0) {
        setTableId(tablesData[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load tables');
    }
  };

  useEffect(() => {
    if (tableId) {
      loadFields();
    }
  }, [tableId]);

  const loadFields = async () => {
    try {
      setLoading(true);
      setError(null);
      const fieldsData = await api.fields.list(tableId!);
      setFields(fieldsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load fields');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tableId || !newFieldName.trim()) return;

    setIsCreating(true);
    try {
      const fieldData: FieldCreate = {
        name: newFieldName.trim(),
        field_type: newFieldType,
        is_required: false,
      };

      await api.fields.create(tableId, fieldData);
      setNewFieldName('');
      setNewFieldType('TEXT');
      loadFields();
    } catch (err: any) {
      setError(err.message || 'Failed to create field');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteField = async (fieldId: string) => {
    if (!confirm('Are you sure you want to delete this field?')) return;

    try {
      await api.fields.delete(fieldId);
      loadFields();
    } catch (err: any) {
      setError(err.message || 'Failed to delete field');
    }
  };

  const handleTableChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedTableId = e.target.value;
    setTableId(selectedTableId);
  };

  return (
    <div className="container">
      <h1 style={{ fontSize: '1.75rem', fontWeight: '700', marginBottom: '1.5rem' }}>
        Fields
      </h1>

      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="form-group">
          <label htmlFor="tableSelect">Select Table</label>
          <select
            id="tableSelect"
            value={tableId || ''}
            onChange={handleTableChange}
          >
            <option value="">Select a table</option>
            {tables.map((table) => (
              <option key={table.id} value={table.id}>
                {table.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {tableId && (
        <div className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Add New Field
          </h2>
          <form onSubmit={handleCreateField}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label htmlFor="newFieldName">Field Name</label>
                <input
                  type="text"
                  id="newFieldName"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  placeholder="Enter field name"
                  required
                />
              </div>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label htmlFor="newFieldType">Field Type</label>
                <select
                  id="newFieldType"
                  value={newFieldType}
                  onChange={(e) => setNewFieldType(e.target.value as any)}
                >
                  <option value="TEXT">Text</option>
                  <option value="NUMBER">Number</option>
                  <option value="DATE">Date</option>
                  <option value="URL">URL</option>
                  <option value="SELECT">Select</option>
                  <option value="TAGS">Tags</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary" disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Add Field'}
              </button>
            </div>
          </form>
        </div>
      )}

      {tableId && fields.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Existing Fields
          </h2>
          <div className="fields-list">
            {fields.map((field) => (
              <div key={field.id} className="field-item">
                <div className="field-info">
                  <div className="field-name">{field.name}</div>
                  <div className="field-type">
                    {field.field_type} {field.is_required && '(Required)'}
                  </div>
                </div>
                <div className="field-actions">
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDeleteField(field.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
