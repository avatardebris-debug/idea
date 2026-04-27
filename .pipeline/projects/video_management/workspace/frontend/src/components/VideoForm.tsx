import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api, type Video, type VideoCreate, type VideoUpdate } from '../api';

export default function VideoForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'draft' | 'scheduled' | 'publishing' | 'published' | 'failed'>('draft');
  const [tags, setTags] = useState('');
  const [publishDate, setPublishDate] = useState('');
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  const [youtubeVideoId, setYoutubeVideoId] = useState('');
  const [customFields, setCustomFields] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isEditing) {
      loadVideo();
    }
  }, [id]);

  const loadVideo = async () => {
    try {
      const video = await api.videos.get(id!);
      setTitle(video.title);
      setDescription(video.description || '');
      setStatus(video.status);
      setTags(video.tags.join(', '));
      setPublishDate(video.publish_date ? video.publish_date.split('T')[0] : '');
      setThumbnailUrl(video.thumbnail_url || '');
      setYoutubeVideoId(video.youtube_video_id || '');
      setCustomFields(video.custom_fields || {});
    } catch (err: any) {
      setError(err.message || 'Failed to load video');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const videoData: VideoCreate | VideoUpdate = {
        title,
        description,
        status,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        publish_date: publishDate || null,
        thumbnail_url: thumbnailUrl || null,
        youtube_video_id: youtubeVideoId || null,
        custom_fields: customFields,
      };

      if (isEditing) {
        await api.videos.update(id!, videoData);
      } else {
        await api.videos.create(videoData);
      }

      setSuccess(true);
      setTimeout(() => navigate('/'), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to save video');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomFieldChange = (key: string, value: string) => {
    setCustomFields(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem' }}>
        <button className="btn btn-secondary" onClick={() => navigate('/')} style={{ marginBottom: '1rem' }}>
          ← Back to Videos
        </button>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700' }}>
          {isEditing ? 'Edit Video' : 'Create New Video'}
        </h1>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">Video saved successfully!</div>}

      <form onSubmit={handleSubmit} className="card">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Enter video title"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter video description"
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as any)}
          >
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="publishing">Publishing</option>
            <option value="published">Published</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="tags">Tags (comma-separated)</label>
          <input
            type="text"
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="python, tutorial, beginner"
          />
        </div>

        <div className="form-group">
          <label htmlFor="publishDate">Publish Date</label>
          <input
            type="date"
            id="publishDate"
            value={publishDate}
            onChange={(e) => setPublishDate(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="thumbnailUrl">Thumbnail URL</label>
          <input
            type="url"
            id="thumbnailUrl"
            value={thumbnailUrl}
            onChange={(e) => setThumbnailUrl(e.target.value)}
            placeholder="https://example.com/image.jpg"
          />
        </div>

        <div className="form-group">
          <label htmlFor="youtubeVideoId">YouTube Video ID</label>
          <input
            type="text"
            id="youtubeVideoId"
            value={youtubeVideoId}
            onChange={(e) => setYoutubeVideoId(e.target.value)}
            placeholder="dQw4w9WgXcQ"
          />
        </div>

        <div className="form-group">
          <label htmlFor="customFields">Custom Fields (JSON)</label>
          <textarea
            id="customFields"
            value={JSON.stringify(customFields, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setCustomFields(parsed);
              } catch {
                // Keep invalid JSON for user to fix
              }
            }}
            placeholder='{"episode": 1, "duration": "10:30"}'
            style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : (isEditing ? 'Update Video' : 'Create Video')}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
