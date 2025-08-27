/**
 * Output Formatter for Demo Node.js CLI
 * Provides standardized output formatting (JSON, YAML, table, CSV)
 */

import chalk from 'chalk';

// Import error handling utilities
import {
  CLIError,
  ValidationError,
  handleError
} from './errors.js';

export class OutputFormatter {
  constructor(options = {}) {
    this.options = {
      colors: options.colors !== false,
      indent: options.indent || 2,
      maxWidth: options.maxWidth || 80,
      ...options
    };
  }

  /**
   * Format data according to the specified format
   */
  format(data, format = 'auto', options = {}) {
    try {
      const formatOptions = { ...this.options, ...options };
      
      // Auto-detect format if not specified
      if (format === 'auto') {
        format = this._detectFormat(data);
      }

      const normalizedFormat = format.toLowerCase();
      
      switch (normalizedFormat) {
        case 'json':
          return this._formatJSON(data, formatOptions);
        case 'yaml':
        case 'yml':
          return this._formatYAML(data, formatOptions);
        case 'table':
          return this._formatTable(data, formatOptions);
        case 'csv':
          return this._formatCSV(data, formatOptions);
        case 'list':
          return this._formatList(data, formatOptions);
        case 'tree':
          return this._formatTree(data, formatOptions);
        case 'raw':
          return String(data);
        default:
          throw new ValidationError(
            `Unsupported format: ${format}`,
            'format',
            format
          );
      }
    } catch (error) {
      if (error instanceof ValidationError) {
        throw error;
      }
      
      // Fallback to raw format on any formatting error
      if (process.env.DEBUG) {
        console.warn(`Formatting failed for ${format}, falling back to raw:`, error.message);
      }
      
      try {
        return String(data);
      } catch (fallbackError) {
        throw new CLIError(
          `Failed to format data: ${error.message}`,
          'FORMAT_ERROR',
          'Unable to format output. Data may be corrupted.',
          1
        );
      }
    }
  }

  /**
   * Auto-detect best format for data
   */
  _detectFormat(data) {
    if (Array.isArray(data)) {
      // Array of objects -> table
      if (data.length > 0 && typeof data[0] === 'object') {
        return 'table';
      }
      // Simple array -> list
      return 'list';
    }
    
    if (typeof data === 'object' && data !== null) {
      return 'json';
    }
    
    return 'raw';
  }

  /**
   * Format as JSON
   */
  _formatJSON(data, options) {
    try {
      const jsonString = JSON.stringify(data, null, options.indent);
      
      if (!options.colors) {
        return jsonString;
      }
      
      // Add syntax highlighting
      return this._highlightJSON(jsonString);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('circular')) {
        // Handle circular references
        try {
          const jsonString = JSON.stringify(data, this._getCircularReplacer(), options.indent);
          if (options.colors) {
            return this._highlightJSON(jsonString);
          }
          return jsonString;
        } catch (fallbackError) {
          throw new CLIError(
            `JSON formatting failed: ${fallbackError.message}`,
            'JSON_FORMAT_ERROR',
            'Unable to format data as JSON. Data contains circular references or unsupported types.',
            1
          );
        }
      }
      
      throw new CLIError(
        `JSON formatting failed: ${error.message}`,
        'JSON_FORMAT_ERROR',
        'Unable to format data as JSON.',
        1
      );
    }
  }

  /**
   * Format as YAML
   */
  _formatYAML(data, options) {
    // Simple YAML serialization (for complex cases, use a YAML library)
    const yamlString = this._toYAML(data, 0);
    
    if (!options.colors) {
      return yamlString;
    }
    
    return this._highlightYAML(yamlString);
  }

  /**
   * Format as table
   */
  _formatTable(data, options) {
    if (!Array.isArray(data)) {
      data = [data];
    }
    
    if (data.length === 0) {
      return options.colors ? chalk.gray('(no data)') : '(no data)';
    }
    
    // Extract headers
    const headers = this._extractHeaders(data);
    const rows = data.map(item => headers.map(header => this._formatCellValue(item[header])));
    
    return this._renderTable(headers, rows, options);
  }

  /**
   * Format as CSV
   */
  _formatCSV(data, options) {
    if (!Array.isArray(data)) {
      data = [data];
    }
    
    if (data.length === 0) {
      return '';
    }
    
    const headers = this._extractHeaders(data);
    const csvRows = [
      headers.join(','),
      ...data.map(item => 
        headers.map(header => this._escapeCsvValue(item[header])).join(',')
      )
    ];
    
    return csvRows.join('\n');
  }

  /**
   * Format as simple list
   */
  _formatList(data, options) {
    if (!Array.isArray(data)) {
      return String(data);
    }
    
    const bullet = options.colors ? chalk.cyan('•') : '•';
    return data.map(item => `${bullet} ${this._formatCellValue(item)}`).join('\n');
  }

  /**
   * Format as tree structure
   */
  _formatTree(data, options, prefix = '', isLast = true) {
    if (typeof data !== 'object' || data === null) {
      return String(data);
    }
    
    const entries = Object.entries(data);
    const lines = [];
    
    entries.forEach(([key, value], index) => {
      const isLastEntry = index === entries.length - 1;
      const connector = isLastEntry ? '└── ' : '├── ';
      const nextPrefix = prefix + (isLastEntry ? '    ' : '│   ');
      
      const keyStr = options.colors ? chalk.cyan(key) : key;
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        lines.push(`${prefix}${connector}${keyStr}`);
        lines.push(this._formatTree(value, options, nextPrefix, isLastEntry));
      } else {
        const valueStr = this._formatCellValue(value);
        lines.push(`${prefix}${connector}${keyStr}: ${valueStr}`);
      }
    });
    
    return lines.join('\n');
  }

  /**
   * Extract headers from array of objects
   */
  _extractHeaders(data) {
    const headerSet = new Set();
    
    data.forEach(item => {
      if (typeof item === 'object' && item !== null) {
        Object.keys(item).forEach(key => headerSet.add(key));
      }
    });
    
    return Array.from(headerSet);
  }

  /**
   * Format cell value for display
   */
  _formatCellValue(value) {
    if (value === null || value === undefined) {
      return this.options.colors ? chalk.gray('null') : 'null';
    }
    
    if (typeof value === 'boolean') {
      const str = String(value);
      return this.options.colors ? 
        (value ? chalk.green(str) : chalk.red(str)) : str;
    }
    
    if (typeof value === 'number') {
      const str = String(value);
      return this.options.colors ? chalk.yellow(str) : str;
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    
    return String(value);
  }

  /**
   * Render table with borders
   */
  _renderTable(headers, rows, options) {
    // Calculate column widths
    const colWidths = headers.map((header, i) => {
      const maxContentWidth = Math.max(
        header.length,
        ...rows.map(row => String(row[i] || '').length)
      );
      return Math.min(maxContentWidth, options.maxWidth / headers.length);
    });
    
    const lines = [];
    
    // Header separator
    const separator = colWidths.map(width => '─'.repeat(width + 2)).join('┬');
    lines.push(`┌${separator}┐`);
    
    // Header row
    const headerRow = headers.map((header, i) => 
      this._padCell(options.colors ? chalk.bold(header) : header, colWidths[i])
    ).join('│');
    lines.push(`│${headerRow}│`);
    
    // Header bottom border
    const headerSep = colWidths.map(width => '─'.repeat(width + 2)).join('┼');
    lines.push(`├${headerSep}┤`);
    
    // Data rows
    rows.forEach(row => {
      const rowStr = row.map((cell, i) => 
        this._padCell(String(cell || ''), colWidths[i])
      ).join('│');
      lines.push(`│${rowStr}│`);
    });
    
    // Bottom border
    const bottomSep = colWidths.map(width => '─'.repeat(width + 2)).join('┴');
    lines.push(`└${bottomSep}┘`);
    
    return lines.join('\n');
  }

  /**
   * Pad cell content to width
   */
  _padCell(content, width) {
    const plainContent = content.replace(/\u001b\[[0-9;]*m/g, ''); // Remove ANSI codes
    const padding = Math.max(0, width - plainContent.length);
    return ` ${content}${' '.repeat(padding)} `;
  }

  /**
   * Escape CSV value
   */
  _escapeCsvValue(value) {
    const str = String(value || '');
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  }

  /**
   * Simple YAML serialization
   */
  _toYAML(obj, indent = 0) {
    const spaces = ' '.repeat(indent);
    
    if (obj === null || obj === undefined) {
      return 'null';
    }
    
    if (typeof obj === 'string') {
      return `"${obj.replace(/"/g, '\\"')}"`;
    }
    
    if (typeof obj === 'number' || typeof obj === 'boolean') {
      return String(obj);
    }
    
    if (Array.isArray(obj)) {
      if (obj.length === 0) return '[]';
      return obj.map(item => `${spaces}- ${this._toYAML(item, indent + 2)}`).join('\n');
    }
    
    if (typeof obj === 'object') {
      const entries = Object.entries(obj);
      if (entries.length === 0) return '{}';
      
      return entries.map(([key, value]) => {
        const yamlValue = this._toYAML(value, indent + 2);
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          return `${spaces}${key}:\n${yamlValue}`;
        }
        return `${spaces}${key}: ${yamlValue}`;
      }).join('\n');
    }
    
    return String(obj);
  }

  /**
   * Highlight JSON syntax
   */
  _highlightJSON(jsonString) {
    return jsonString
      .replace(/"([^"]+)":/g, (match, key) => `${chalk.blue(`"${key}"`)}:`)
      .replace(/:\s*"([^"]*)"/g, (match, value) => `: ${chalk.green(`"${value}"`)}`)
      .replace(/:\s*(\d+)/g, (match, num) => `: ${chalk.yellow(num)}`)
      .replace(/:\s*(true|false)/g, (match, bool) => 
        `: ${bool === 'true' ? chalk.green(bool) : chalk.red(bool)}`
      )
      .replace(/:\s*null/g, `: ${chalk.gray('null')}`);
  }

  /**
   * Highlight YAML syntax
   */
  _highlightYAML(yamlString) {
    return yamlString
      .replace(/^(\s*)([^:\s]+):/gm, (match, indent, key) => 
        `${indent}${chalk.blue(key)}:`
      )
      .replace(/:\s*"([^"]*)"/g, (match, value) => `: ${chalk.green(`"${value}"`)}`)
      .replace(/:\s*(\d+)/g, (match, num) => `: ${chalk.yellow(num)}`)
      .replace(/:\s*(true|false)/g, (match, bool) => 
        `: ${bool === 'true' ? chalk.green(bool) : chalk.red(bool)}`
      );
  }
}

// Global formatter instance
export const formatter = new OutputFormatter();

// Convenience methods
export const formatOutput = (data, format, options) => 
  formatter.format(data, format, options);

export const formatTable = (data, options) => 
  formatter.format(data, 'table', options);

export const formatJSON = (data, options) => 
  formatter.format(data, 'json', options);

export const formatList = (data, options) => 
  formatter.format(data, 'list', options);

// Helper for commands to add standard format options
export function addFormatOption(command) {
  return command
    .option('--format <type>', 'Output format (json|yaml|table|csv|list|tree)', 'auto')
    .option('--no-colors', 'Disable colored output')
    .option('--max-width <width>', 'Maximum table width', '80');
}

// Helper to output formatted data based on command options
export function outputFormatted(data, options = {}) {
  const format = options.format || 'auto';
  const formatterOptions = {
    colors: options.colors !== false,
    maxWidth: parseInt(options.maxWidth) || 80
  };
  
  const output = formatter.format(data, format, formatterOptions);
  console.log(output);
}

export default OutputFormatter;