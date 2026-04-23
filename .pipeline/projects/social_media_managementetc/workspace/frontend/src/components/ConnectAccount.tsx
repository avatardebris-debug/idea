import React, { useState } from 'react'

export function ConnectAccount() {
  const [showModal, setShowModal] = useState(false)
  const [platform, setPlatform] = useState<'twitter' | 'instagram' | null>(null)

  const handleConnect = async (platform: 'twitter' | 'instagram') => {
    setPlatform(platform)
    // In production, this would redirect to OAuth
    alert(`Redirecting to ${platform} OAuth...`)
    setShowModal(false)
  }

  return (
    <div>
      <button onClick={() => setShowModal(true)} style={{ padding: '8px 16px', backgroundColor: '#1DA1F2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        Connect Account
      </button>

      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', maxWidth: '400px', width: '100%' }}>
            <h2 style={{ marginBottom: '20px' }}>Connect Social Account</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button onClick={() => handleConnect('twitter')} style={{ padding: '12px', backgroundColor: '#1DA1F2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}>
                Connect Twitter
              </button>
              <button onClick={() => handleConnect('instagram')} style={{ padding: '12px', backgroundColor: '#E1306C', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}>
                Connect Instagram
              </button>
            </div>
            <button onClick={() => setShowModal(false)} style={{ marginTop: '20px', padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', width: '100%' }}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
