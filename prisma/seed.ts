import { PrismaClient } from '@prisma/client';
import { faker } from '@faker-js/faker';

const prisma = new PrismaClient();

async function main() {
  console.log(`Start seeding ...`);

  // Clear existing data (optional, for development)
  await prisma.insight.deleteMany();
  await prisma.dataStream.deleteMany();
  await prisma.user.deleteMany();
  await prisma.workspace.deleteMany();

  // Create Workspaces
  const workspace1 = await prisma.workspace.create({
    data: { name: 'Aether Global Finance' },
  });
  const workspace2 = await prisma.workspace.create({
    data: { name: 'Quantum Analytics' },
  });

  // Create Users (with mock Clerk IDs)
  const user1 = await prisma.user.create({
    data: {
      clerkId: 'user_2aB3cD4eF5g6H7i8J9k0L1m2N3o4P5q6R7s8T9u0', // Mock Clerk ID
      email: 'alice@aether.com',
      name: 'Alice Smith',
      workspaceId: workspace1.id,
    },
  });
  const user2 = await prisma.user.create({
    data: {
      clerkId: 'user_xB7yC8zD9eF0g1H2I3j4K5l6M7n8O9p0Q1r2S3t4', // Mock Clerk ID
      email: 'bob@aether.com',
      name: 'Bob Johnson',
      workspaceId: workspace1.id,
    },
  });

  // Generate Global Sales DataStream (realistic, with Q3 dip simulation)
  const generateSalesData = (startDate: Date, numDays: number, initialValue: number, dipStartMonth: number, dipEndMonth: number) => {
    const data = [];
    let currentValue = initialValue;
    for (let i = 0; i < numDays; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);

      let trendFactor = 0;
      if (date.getMonth() + 1 >= dipStartMonth && date.getMonth() + 1 <= dipEndMonth) {
        // Simulate a Q3 dip (July, Aug, Sep)
        trendFactor = faker.number.float({ min: -0.05, max: -0.01 });
      } else {
        trendFactor = faker.number.float({ min: -0.005, max: 0.015 });
      }

      currentValue = currentValue * (1 + trendFactor) + faker.number.float({ min: -5000, max: 5000 });
      currentValue = Math.max(10000, currentValue); // Ensure value doesn't drop too low

      data.push({
        date: date.toISOString().split('T')[0],
        value: Math.round(currentValue),
      });
    }
    return data;
  };

  const salesDataPoints = generateSalesData(new Date('2023-01-01'), 365, 1000000, 7, 9); // One year of data, Q3 dip
  
  const globalSalesStream = await prisma.dataStream.create({
    data: {
      workspaceId: workspace1.id,
      name: 'Global Sales',
      dataType: 'revenue_usd',
      data: salesDataPoints as any, // Prisma expects Json type
      timestamp: new Date(),
    },
  });

  console.log(`Seeding finished.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
