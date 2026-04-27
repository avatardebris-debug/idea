import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, type Video, type PaginatedResponse } from '../api';

interface VideoListProps {
  tableId: string;
}

export default function VideoList({ tableId }: VideoListProps) {
  const navigate = useNavigate();
  const [videos, setVideos] = useState<Video[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { page, page_size: pageSize };
      if (search) params.search = search;
      if (status) params.status = status;

      const data = await api.videos.list(params);
      setVideos(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch videos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, [page, pageSize, search, status]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this video?')) return;

    try {
      await api.videos.delete(id);
      fetchVideos();
    } catch (err: any) {
      alert(err.message || 'Failed to delete video');
    }
  };

  const handleEdit = (id: string) => {
    navigate(`/videos/${id}/edit`);
  };

  const handleCreate = () => {
    navigate('/videos/new');
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700' }}>Videos</h1>
        <button className="btn btn-primary" onClick={handleCreate}>
          + Add Video
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search videos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="scheduled">Scheduled</option>
          <option value="publishing">Publishing</option>
          <option value="published">Published</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading videos...</div>
      ) : videos.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
            No videos found. {total === 0 ? 'Click "Add Video" to create one.' : 'Try adjusting your filters.'}
          </p>
        </div>
      ) : (
        <>
          <div className="video-grid">
            {videos.map((video) => (
              <div key={video.id} className="video-card">
                <h3>{video.title}</h3>
                <p>{video.description || 'No description'}</p>
                <div className="tags">
                  {video.tags.map((tag) => (
                    <span key={tag} className="tag">#{tag}</span>
                  ))}
                </div>
                <span className={`status-badge status-${video.status}`}>
                  {video.status}
                </span>
                <div className="actions">
                  <button className="btn btn-secondary" onClick={() => handleEdit(video.id)}>
                    Edit
                  </button>
                  <button className="btn btn-danger" onClick={() => handleDelete(video.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
            >
              Previous
            </button>
            <span>
              Page {page} of {totalPages || 1} ({total} total)
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
