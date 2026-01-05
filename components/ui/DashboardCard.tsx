"use client"; // This component might be client-side due to interactions/Framer Motion

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils'; // A utility for conditionally joining class names

// Design Tokens Used:
// - spacing.6 (24px padding)
// - colors.gray.50, gray.800 (backgrounds)
// - colors.gray.200, gray.700 (borders)
// - boxShadow.md (card elevation)
// - colors.primary.500 (example icon color)
// - fontSize.fluid-xl (heading)
// - fontSize.fluid-sm (metadata)
// - transitionDuration.250
// - transitionTimingFunction.ease-out-cubic

interface DashboardCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOutCubic', // Using the custom cubic-bezier
    },
  },
};

export function DashboardCard({
  title,
  value,
  description,
  icon,
  className,
  children,
}: DashboardCardProps) {
  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      className={cn(
        "relative flex flex-col p-6 rounded-2xl shadow-md",
        "bg-white dark:bg-gray-800",
        "border border-gray-200 dark:border-gray-700",
        "transition-all duration-250 ease-out-cubic", // Apply global transition
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-fluid-xl font-semibold text-primary-700 dark:text-primary-300">
          {title}
        </h3>
        {icon && <div className="text-primary-500 dark:text-accent-400 text-3xl">{icon}</div>}
      </div>
      <div className="flex-grow">
        {children || (
          <>
            <p className="text-fluid-5xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              {value}
            </p>
            {description && (
              <p className="text-fluid-sm text-gray-600 dark:text-gray-400">
                {description}
              </p>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}
