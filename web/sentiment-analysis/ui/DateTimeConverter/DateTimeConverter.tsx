import React from "react";
import { format, isToday, isYesterday } from "date-fns";

/**
 * Defaults to - Jan 20, 2025, 5:46:00 PM
 * MMM d, yyyy - Jan 20, 2025
 */

interface DateTimeConverterProps {
  /** The datetime string to convert (e.g. "2025-01-20T17:46:00") */
  dateTime: string;
  /**
   * The format string using date-fns formatting tokens (e.g. "MMM d, yyyy, h:mm a").
   * Defaults to "PPpp".
   */
  formatStr?: string;
  /**
   * If true, the component will display "today" or "yesterday" when applicable.
   */
  relative?: boolean;
}

/**
 * DateTimeConverter converts a datetime string into any specified format.
 * It optionally returns "today" or "yesterday" if the relative prop is true.
 *
 * @param props - DateTimeConverterProps
 */
export function DateTimeConverter(props: DateTimeConverterProps) {
  const { dateTime, formatStr = "PPpp", relative = false } = props;
  const date = new Date(dateTime);

  // If the provided dateTime string is invalid, show an error message.
  if (isNaN(date.getTime())) {
    return <span>Invalid Date</span>;
  }

  let displayText: string;

  // When the relative flag is true, check if the date is today or yesterday.
  if (relative) {
    if (isToday(date)) {
      displayText = "today";
    } else if (isYesterday(date)) {
      displayText = "yesterday";
    } else {
      displayText = format(date, formatStr);
    }
  } else {
    displayText = format(date, formatStr);
  }

  return <span>{displayText}</span>;
}
