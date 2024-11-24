import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/react';
import AudioRecorder from '../components/AudioRecorder';

describe('AudioRecorder', () => {
  it('should render start recording button', () => {
    const { getByText } = render(<AudioRecorder />);
    expect(getByText('Start Recording')).toBeDefined();
  });

  it('should toggle recording state when button is clicked', async () => {
    const { getByText } = render(<AudioRecorder />);
    const button = getByText('Start Recording');
    
    fireEvent.click(button);
    await waitFor(() => {
      expect(getByText('Stop Recording')).toBeDefined();
    });
    
    fireEvent.click(getByText('Stop Recording'));
    await waitFor(() => {
      expect(getByText('Start Recording')).toBeDefined();
    });
  });
});
