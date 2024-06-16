import React, { Suspense } from 'react';
import UserPageContent from './user-page-content';

const UserPage = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <UserPageContent />
  </Suspense>
);

export default UserPage;
