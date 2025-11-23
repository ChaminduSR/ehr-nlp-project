import { useState, useEffect } from 'react';
import { Button } from '../ehr/Button';
import { Textarea } from '../ehr/Input';
import { AutoSaveIndicator } from '../ehr/AutoSaveIndicator';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';
import { api } from '../../services/api';
import { useApp } from '../../contexts/AppContext';

type SaveStatus = 'saving' | 'saved' | 'error';
type NoteStatus = 'draft' | 'finalized';

export function MedicalNote() {
  const { currentPatient, currentVisit, setError, isLoading, setIsLoading } = useApp();
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [noteStatus, setNoteStatus] = useState<NoteStatus>('draft');
  const [noteId, setNoteId] = useState<number | null>(null);
  const [noteText, setNoteText] = useState('');
  const [nlpResults, setNlpResults] = useState<{
    entities_extracted: number;
    processing_time_ms: number;
  } | null>(null);

  // Build complete note text from all fields
  const buildNoteText = () => {
    const sections = [
      noteText.trim() ? noteText : '',
    ];
    return sections.filter(s => s).join('\n\n');
  };

  // Auto-save every 30 seconds
  useEffect(() => {
    if (noteStatus === 'draft' && currentVisit && noteText.trim()) {
      const interval = setInterval(() => {
        handleAutoSave();
      }, 30000); // 30 seconds

      return () => clearInterval(interval);
    }
  }, [noteText, noteStatus, currentVisit]);

  const handleAutoSave = async () => {
    if (!currentVisit) {
      setError('No active visit. Please create a visit first.');
      return;
    }

    setSaveStatus('saving');

    try {
      const text = buildNoteText();
      const response = await api.saveDraft(currentVisit.id, text);

      if (!noteId) {
        setNoteId(response.note_id);
      }

      setSaveStatus('saved');
      setLastSaved(new Date(response.draft_saved_at));
      console.log('Auto-saved draft:', response);
    } catch (err: any) {
      setSaveStatus('error');
      setError(err.message || 'Failed to save draft');
      console.error('Auto-save error:', err);
    }
  };

  const handleFinalize = async () => {
    if (!noteId) {
      alert('Please save a draft first before finalizing.');
      return;
    }

    if (!window.confirm('Are you sure you want to finalize this note? Finalized notes cannot be edited and will be processed with NLP.')) {
      return;
    }

    setIsLoading(true);
    setSaveStatus('saving');

    try {
      const text = buildNoteText();
      const response = await api.finalizeNote(noteId, text);

      setNoteStatus('finalized');
      setSaveStatus('saved');
      setLastSaved(new Date(response.signed_at));
      setNlpResults({
        entities_extracted: response.entities_extracted,
        processing_time_ms: response.processing_time_ms,
      });

      alert(`Medical note finalized successfully!\nEntities extracted: ${response.entities_extracted}\nProcessing time: ${response.processing_time_ms}ms`);
    } catch (err: any) {
      setSaveStatus('error');
      setError(err.message || 'Failed to finalize note');
      alert('Error finalizing note: ' + (err.message || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveDraft = () => {
    handleAutoSave();
  };

  // noteStatus is used directly in the JSX below; no separate `isFinalized` variable needed

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1>Medical Note</h1>
          <p className="text-[#333333] mt-2">Create comprehensive rheumatology assessment</p>
        </div>
        <AutoSaveIndicator status={saveStatus} lastSaved={lastSaved || undefined} />
      </div>

      {/* Patient Info */}
      {!currentPatient && (
        <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded">
          <p className="text-yellow-800">No patient selected. Please select a patient from Patient Management first.</p>
        </div>
      )}

      {!currentVisit && currentPatient && (
        <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded">
          <p className="text-yellow-800">No active visit. Please create a visit for this patient first.</p>
        </div>
      )}

      {currentPatient && currentVisit && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Patient Information</CardTitle>
                {noteStatus === 'finalized' ? (
                  <span className="px-4 py-2 bg-[#00AA00] text-white rounded">
                    Finalized {nlpResults && `(${nlpResults.entities_extracted} entities)`}
                  </span>
                ) : (
                  <span className="px-4 py-2 bg-[#FF9900] text-white rounded">
                    Draft
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-[#333333]">MRN</div>
                  <div className="font-medium">{currentPatient.mrn}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Patient Name</div>
                  <div className="font-medium">{currentPatient.first_name} {currentPatient.last_name}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Visit Date</div>
                  <div className="font-medium">{currentVisit.visit_date}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Visit Type</div>
                  <div className="font-medium">{currentVisit.visit_type}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Note Form */}
          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <Card>
              <CardHeader>
                <CardTitle>Medical Note</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  id="note-text"
                  placeholder="Document the medical note here. Include chief complaint, history of present illness, physical exam findings, assessment, and plan..."
                  rows={20}
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  disabled={noteStatus === 'finalized'}
                />
                <p className="text-sm text-[#666666] mt-2">
                  Note will be auto-saved every 30 seconds while in draft status.
                  When finalized, the note will be processed with NLP to extract medical entities.
                </p>
              </CardContent>
            </Card>

            {nlpResults && (
              <Card>
                <CardHeader>
                  <CardTitle>NLP Processing Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-[#333333]">Entities Extracted</div>
                      <div className="font-medium text-lg">{nlpResults.entities_extracted}</div>
                    </div>
                    <div>
                      <div className="text-sm text-[#333333]">Processing Time</div>
                      <div className="font-medium text-lg">{nlpResults.processing_time_ms.toFixed(2)}ms</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            {noteStatus !== 'finalized' && (
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="draft"
                  fullWidth
                  onClick={handleSaveDraft}
                  disabled={isLoading || !noteText.trim()}
                >
                  Save Draft Now
                </Button>
                <Button
                  type="button"
                  variant="success"
                  fullWidth
                  onClick={handleFinalize}
                  disabled={isLoading || !noteId}
                >
                  {isLoading ? 'Processing...' : 'Finalize Note & Run NLP'}
                </Button>
              </div>
            )}

            {noteStatus === 'finalized' && (
              <div className="p-4 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded">
                <p className="text-center">
                  This note has been finalized and processed with NLP.
                  Finalized notes cannot be edited.
                </p>
              </div>
            )}
          </form>
        </>
      )}
    </div>
  );
}
