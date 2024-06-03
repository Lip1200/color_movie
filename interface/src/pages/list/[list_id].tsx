import dynamic from 'next/dynamic';

const ListPage = dynamic(() => import('@/components/Lists/ListsPage'), {
  ssr: false,
});

const ListDetailsPage = () => {
  return <ListPage />;
};

export default ListDetailsPage;
