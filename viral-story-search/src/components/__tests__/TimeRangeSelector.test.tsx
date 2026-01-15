import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TimeRangeSelector from '../TimeRangeSelector';

describe('TimeRangeSelector Component', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render all time range options', () => {
    render(
      <TimeRangeSelector
        selected="1d"
        onChange={mockOnChange}
      />
    );

    // Check that all required time range options are displayed
    expect(screen.getByText('1 Hour')).toBeInTheDocument();
    expect(screen.getByText('1 Day')).toBeInTheDocument();
    expect(screen.getByText('10 Days')).toBeInTheDocument();
    expect(screen.getByText('100 Days')).toBeInTheDocument();
  });

  it('should highlight the selected time range', () => {
    render(
      <TimeRangeSelector
        selected="1d"
        onChange={mockOnChange}
      />
    );

    const selectedButton = screen.getByText('1 Day');
    const unselectedButton = screen.getByText('1 Hour');

    // Selected button should have blue background
    expect(selectedButton).toHaveClass('bg-blue-600', 'text-white', 'border-blue-600');
    
    // Unselected button should have white background
    expect(unselectedButton).toHaveClass('bg-white', 'text-gray-700', 'border-gray-300');
  });

  it('should call onChange when a time range is selected', () => {
    render(
      <TimeRangeSelector
        selected="1d"
        onChange={mockOnChange}
      />
    );

    const hourButton = screen.getByText('1 Hour');
    fireEvent.click(hourButton);

    expect(mockOnChange).toHaveBeenCalledWith('1h');
  });

  it('should display tooltips with descriptions', () => {
    render(
      <TimeRangeSelector
        selected="1d"
        onChange={mockOnChange}
      />
    );

    const hourButton = screen.getByText('1 Hour');
    expect(hourButton).toHaveAttribute('title', 'Posts from the last hour');
  });

  it('should use default options when none provided', () => {
    render(
      <TimeRangeSelector
        selected="1d"
        onChange={mockOnChange}
      />
    );

    // Should render default options
    expect(screen.getByText('1 Hour')).toBeInTheDocument();
    expect(screen.getByText('1 Day')).toBeInTheDocument();
    expect(screen.getByText('10 Days')).toBeInTheDocument();
    expect(screen.getByText('100 Days')).toBeInTheDocument();
  });
});